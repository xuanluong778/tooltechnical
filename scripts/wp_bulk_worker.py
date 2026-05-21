import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _safe_post_title(post: dict) -> str:
    t = post.get("title") or {}
    if isinstance(t, dict):
        return str(t.get("rendered") or "").strip()
    return str(t or "").strip()


def _safe_post_content(post: dict) -> str:
    c = post.get("content") or {}
    if isinstance(c, dict):
        return str(c.get("rendered") or "").strip()
    return str(c or "").strip()


def _run_job_payload(job_id: str, payload: dict) -> None:
    from app.services.job_store import fail_job, finish_job, update_job
    from app.services.wp_bulk_update import (
        AddonSpec,
        MARKER_END,
        MARKER_START,
        build_wp_session,
        generate_addon_html,
        has_marker,
        normalize_wp_base_url,
        wp_auth_check,
        wp_list_posts,
        wp_update_post_content,
        wrap_marker,
    )

    def hook(p: int, msg: str) -> None:
        update_job(job_id, progress=int(p), message=str(msg))

    wp_url = str(payload.get("wp_url") or "").strip()
    username = str(payload.get("username") or "").strip()
    app_password = str(payload.get("app_password") or "").strip()
    post_type = str(payload.get("post_type") or "posts").strip() or "posts"
    status = str(payload.get("status") or "publish").strip() or "publish"
    limit = int(payload.get("limit") or 200)
    per_page = int(payload.get("per_page") or 30)
    goal = str(payload.get("goal") or "").strip()
    max_words = int(payload.get("max_words") or 350)
    dry_run = bool(payload.get("dry_run"))

    wp_base = normalize_wp_base_url(wp_url)

    # Auth attempts: raw and strip spaces (WP app passwords often copied with spaces)
    session = None
    for strip_spaces in (False, True):
        s = build_wp_session(username, app_password, strip_spaces=strip_spaces)
        try:
            wp_auth_check(session=s, wp_base=wp_base)
            session = s
            break
        except Exception:
            continue
    if session is None:
        raise RuntimeError("WP auth failed. Check username + application password.")

    spec = AddonSpec(goal=goal or "Bổ sung FAQ + kết luận + CTA", max_words=max_words)

    updated: list[dict] = []
    skipped: list[dict] = []
    failed: list[dict] = []

    try:
        hook(1, "Listing posts…")
        page = 1
        seen = 0
        total_pages = None
        while True:
            items, total_pages = wp_list_posts(
                session=session,
                wp_base=wp_base,
                post_type=post_type,
                status=status,
                per_page=per_page,
                page=page,
            )
            if not items:
                break
            for post in items:
                if seen >= limit:
                    break
                seen += 1

                post_id = int(post.get("id") or 0)
                title = _safe_post_title(post)
                content_html = _safe_post_content(post)
                link = str(post.get("link") or "").strip()

                pct = int(round((seen / max(1, limit)) * 95))
                hook(max(1, min(95, pct)), f"Processing {seen}/{limit}: post_id={post_id}")

                if not post_id or not content_html:
                    skipped.append({"post_id": post_id, "link": link, "reason": "missing_content_or_id"})
                    continue
                if has_marker(content_html):
                    skipped.append({"post_id": post_id, "link": link, "reason": "already_has_marker"})
                    continue

                try:
                    addon_html = generate_addon_html(title=title, existing_html=content_html, spec=spec)
                    if not addon_html.strip():
                        skipped.append({"post_id": post_id, "link": link, "reason": "empty_addon"})
                        continue

                    new_html = (content_html.rstrip() + wrap_marker(addon_html)).strip()
                    if dry_run:
                        updated.append(
                            {
                                "post_id": post_id,
                                "link": link,
                                "dry_run": True,
                                "marker": {"start": MARKER_START, "end": MARKER_END},
                                "addon_preview": addon_html[:900],
                            }
                        )
                        continue

                    wp_update_post_content(
                        session=session,
                        wp_base=wp_base,
                        post_id=post_id,
                        post_type=post_type,
                        new_content_html=new_html,
                    )
                    updated.append({"post_id": post_id, "link": link, "dry_run": False})
                except Exception as exc:
                    failed.append({"post_id": post_id, "link": link, "error": str(exc)[:800]})

            if seen >= limit:
                break
            page += 1
            if total_pages is not None and page > total_pages:
                break

        hook(98, "Finalizing…")
        finish_job(
            job_id,
            result={
                "ok": True,
                "dry_run": dry_run,
                "wp_base": wp_base,
                "post_type": post_type,
                "status": status,
                "limit": limit,
                "stats": {"updated": len(updated), "skipped": len(skipped), "failed": len(failed)},
                "updated": updated[:200],
                "skipped": skipped[:200],
                "failed": failed[:200],
                "note": "Nếu updated/skipped/failed dài, kết quả đã bị cắt còn 200 dòng để tránh quá tải.",
            },
        )
    except Exception:
        import traceback

        fail_job(job_id, error=traceback.format_exc())


def main() -> None:
    from app.services.job_store import (
        claim_next_pending_job,
        ensure_job_schema,
        mark_stale_jobs_failed,
        update_job,
        fail_job,
    )

    ensure_job_schema()

    poll = float(os.getenv("JOB_WORKER_POLL_SECONDS", "1.2"))
    watchdog = int(os.getenv("JOB_WATCHDOG_SECONDS", "300"))
    hard_timeout = int(os.getenv("JOB_TOTAL_HARD_TIMEOUT", "900"))

    print("wp_bulk_worker: started", flush=True)
    while True:
        try:
            mark_stale_jobs_failed(stale_seconds=watchdog)
            job = claim_next_pending_job(job_type="wp_bulk_update")
            if not job:
                time.sleep(poll)
                continue

            payload = job.payload or {}
            update_job(job.job_id, state="RUNNING", progress=max(1, job.progress), message="Starting worker")

            import multiprocessing as mp

            p = mp.Process(target=_run_job_payload, args=(job.job_id, payload), daemon=False)
            p.start()
            t0 = time.time()
            while p.is_alive():
                if time.time() - t0 > hard_timeout:
                    try:
                        p.terminate()
                    except Exception:
                        pass
                    fail_job(job.job_id, error=f"Hard timeout >{hard_timeout}s (worker killed process)")
                    break
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("wp_bulk_worker: stop", flush=True)
            return
        except Exception as exc:
            print(f"wp_bulk_worker: error: {exc}", flush=True)
            time.sleep(2.0)


if __name__ == "__main__":
    main()

