# 07 — Schema Generator (JSON-LD)

## URL

`GET /schema`

## Mục tiêu

Tạo và xem trước markup Schema.org (JSON-LD) từ form thủ công hoặc phân tích URL/HTML.

## File chính

| Loại | Path |
|------|------|
| Template | `templates/schema_tool.html` (~1600+ dòng) |
| API | endpoints trong `pages.py` / integrations |

## Tab trong trang

| Tab | `data-panel` | Chức năng |
|-----|--------------|-----------|
| **Tạo từ form** | `manual` | Organization, LocalBusiness, Article, Product, FAQ, HowTo… |
| **Từ URL / HTML** | `analyze` | Parse trang + căn SERP → sinh schema |

## API

| Method | Path (tham khảo) |
|--------|------------------|
| POST | `/schema-generator` |
| GET/POST | `/api/schema-preview` |

## UI

- Layout 2 cột: form trái / preview JSON phải
- Chọn loại schema (`schema-kind-select`)

## Trạng thái

**Hoàn chỉnh**

## Liên kết

- [03-technical-seo-tool.md](./03-technical-seo-tool.md)
