# 03 — Phân tích Technical SEO

## URL

`GET /tool`

## Mục tiêu

Crawl website, chạy checklist technical SEO (15+ nhóm / pillars), lưu dự án theo user, xuất báo cáo.

## File chính

| Loại | Path |
|------|------|
| Template | `templates/seo_tool.html` |
| Router analyze | `app/routers/analyze.py` |
| Analyzer | `app/services/analyzer.py`, `app/seo_pipeline/*` |
| Checklist pillars | `app/services/seo_fifteen_pillars.py` |
| Projects | `app/routers/projects.py` |

## Layout UI

| Vùng | Nội dung |
|------|----------|
| Sidebar trái | Menu checklist / pillars (icon + nhóm lỗi) |
| Giữa | Form URL, kết quả quét, chi tiết issue |
| Sidebar phải | Dự án đã quét |

## API chính

| Method | Path |
|--------|------|
| POST | `/analyze`, `/analyze/technical` |
| CRUD | `/projects` (SEO projects) |

## Loại issue (ví dụ)

- Broken internal links, redirect chain
- Robots / sitemap
- HTTPS, HTTP status
- Title, meta, canonical, H1, lang
- Images / alt, indexability, cloaking, JS rendering

## Công nghệ crawl

- **Playwright** (render JS)
- **requests** + **BeautifulSoup** (parse HTML)
- Catalog audit: `_load_technical_audit_catalog()` trong `pages.py`

## Trạng thái

**Module lõi — rất đầy đủ**

## Liên kết

- [02-dashboard-report.md](./02-dashboard-report.md)
- [04-seo-url-score.md](./04-seo-url-score.md)
- [00-overview-stack.md](./00-overview-stack.md)
