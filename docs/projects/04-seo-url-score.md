# 04 — Chấm điểm SEO (URL Scoreboard)

## URL

`GET /tool/seo-score`

## Mục tiêu

Chấm điểm và báo cáo tối ưu **theo từng URL** (on-page / URL-level), UI sidebar checklist tương tự Technical.

## File chính

| Loại | Path |
|------|------|
| Template | `templates/seo_url_score.html` |
| Service | `app/services/url_seo_scoreboard.py` |
| Report | `app/services/url_seo_optimization_report.py` |
| Schema | `app/schemas/url_scoreboard.py` |

## API

| Method | Path |
|--------|------|
| POST | `/analyze/url-seo-scoreboard` |

## Khác với `/tool`

| | Technical `/tool` | SEO Score `/tool/seo-score` |
|--|-------------------|------------------------------|
| Trọng tâm | Crawl site, lỗi kỹ thuật toàn site | Điểm / checklist một URL |
| Template | `seo_tool.html` | `seo_url_score.html` |

## Trạng thái

**Hoàn chỉnh**

## Liên kết

- [03-technical-seo-tool.md](./03-technical-seo-tool.md)
