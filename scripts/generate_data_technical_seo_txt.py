"""Generate data/Technical-SEO.txt from CHECKLIST_TITLE_VI (full checklist for /report)."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from app.seo_pipeline.constants import CHECKLIST_TITLE_VI, TECH_CHECKLIST_BY_TYPE  # noqa: E402
from app.services.report_builder import GROUP_DISPLAY_ORDER  # noqa: E402

GROUP_HINT = {
    "GSC": "Quét kỹ thuật onsite (crawler nội bộ), không phải export Search Console",
    "Robots": "robots.txt crawler",
    "Sitemap": "sitemap xml loc",
    "Security": "HTTPS TLS certificate",
    "Onpage": "meta title H1 canonical schema",
    "Images": "image alt text",
    "International": "hreflang html lang international",
    "Mobile": "mobile viewport",
    "Speed": "pagespeed Core Web Vitals",
    "Video": "video embed schema",
    "General": "technical audit",
    "Crawl quality": "crawl budget quality",
}

EXTRA_ROWS: list[tuple[str, str, str]] = [
    ("Log server và mã lỗi 4xx/5xx tổng hợp", "Chưa rõ", "Security — theo dõi log, alert khi spike 5xx."),
    ("Structured data (JSON-LD) hợp lệ Rich Results", "Chưa rõ", "Onpage — Rich Results Test, không lỗi critical."),
    ("Pagination rel=prev/next hoặc chiến lược thay thế rõ ràng", "Chưa rõ", "Onpage — tránh orphan page và trùng lặp phân trang."),
    ("DNS / CDN / TTL và độ ổn định origin", "Chưa rõ", "Security — không NXDOMAIN, không cấu hình CDN chặn bot."),
    ("Backup và rollback khi deploy ảnh hưởng SEO", "Chưa rõ", "General — quy trình release an toàn."),
]


def _grp_rank(group: str) -> int:
    try:
        return GROUP_DISPLAY_ORDER.index(group)
    except ValueError:
        return 999


def main() -> None:
    items = sorted(
        CHECKLIST_TITLE_VI.items(),
        key=lambda kv: (_grp_rank(TECH_CHECKLIST_BY_TYPE.get(kv[0], "General")), kv[0]),
    )
    out: list[str] = ["CHECKLIST\tĐÁNH GIÁ\tDẪN CHỨNG"]
    for typ, vi in items:
        grp = TECH_CHECKLIST_BY_TYPE.get(typ, "General")
        hint = GROUP_HINT.get(grp, grp)
        ev = f"{hint} — Loại quét: {typ}."
        out.append(f"{vi}\tChưa rõ\t{ev}")
    for ck, dg, ev in EXTRA_ROWS:
        out.append(f"{ck}\t{dg}\t{ev}")
    path = _ROOT / "data" / "Technical-SEO.txt"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote {len(out) - 1} data rows to {path}")


if __name__ == "__main__":
    main()
