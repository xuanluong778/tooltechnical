import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run_job_payload(job_id: str, payload: dict) -> None:
    from app.services.job_store import fail_job, finish_job, update_job
    from app.services.keyword_cluster_pipeline import build_keyword_cluster_api_response

    keywords = payload.get("keywords") or []
    fetch_serp = bool(payload.get("fetch_serp"))
    if os.getenv("BENCH_FAST", "0").lower() in ("1", "true", "yes"):
        fetch_serp = False

    def hook(p: int, msg: str) -> None:
        update_job(job_id, progress=int(p), message=str(msg))

    try:
        res = build_keyword_cluster_api_response(
            keywords,
            fetch_serp=fetch_serp,
            brand_host_hint=payload.get("brand_host_hint"),
            serp_country=payload.get("serp_country"),
            serp_language=payload.get("serp_language"),
            serp_device=payload.get("serp_device"),
            cluster_strictness=payload.get("cluster_strictness"),
            progress_hook=hook,
        )
        finish_job(job_id, result=res)
    except Exception as exc:
        import traceback

        fail_job(job_id, error=traceback.format_exc())
        return


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
    hard_timeout = int(os.getenv("JOB_TOTAL_HARD_TIMEOUT", "420"))  # hard kill per job

    print("keyword_cluster_worker: started", flush=True)
    while True:
        try:
            mark_stale_jobs_failed(stale_seconds=watchdog)
            job = claim_next_pending_job(job_type="keyword_cluster")
            if not job:
                time.sleep(poll)
                continue

            payload = job.payload or {}
            update_job(job.job_id, state="RUNNING", progress=max(1, job.progress), message="Starting worker")

            # Hard timeout via subprocess.
            import multiprocessing as mp

            # Must NOT be daemon: clustering uses ProcessPoolExecutor internally.
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
            print("keyword_cluster_worker: stop", flush=True)
            return
        except Exception as exc:
            # Avoid worker crash loop; sleep a bit.
            print(f"keyword_cluster_worker: error: {exc}", flush=True)
            time.sleep(2.0)


if __name__ == "__main__":
    main()

