# 06 — Từ khóa (Keyword Research)

## URL

`GET /keywords/tools/research`

## Mục tiêu

Nghiên cứu từ khóa, gợi ý, gom nhóm (cluster SERP), lưu project server, export Excel/Sheets.

## File chính

| Loại | Path |
|------|------|
| Template | `templates/keyword_research.html` |
| Router | `app/routers/keywords.py` |
| Pipeline | `app/services/keyword_research_pipeline.py` |
| Cluster | `app/services/keyword_cluster_pipeline.py`, `keyword_clusterer.py` |
| Models | `app/models/keyword_research_project.py`, `keyword_cluster_*.py` |
| Volume | `app/services/search_volume.py`, `volume_providers/*` |
| Docs nguồn data | [../keyword-data-sources.md](../keyword-data-sources.md) |

## Tab trong trang

| Tab | `data-tab` | Chức năng |
|-----|------------|-----------|
| **Phân tích từ khóa** | `analysis` | Chạy research, bảng volume/CPC, lưu project |
| **Keyword Suggestion** | `suggest` | Gợi ý từ khóa liên quan |
| **Gom nhóm từ khóa** | `group` | Cluster SERP (sync/async), intent, export |

## API chính (prefix `/keywords`)

| Nhóm | Mô tả |
|------|--------|
| Research | Tạo/list/xóa project, chạy phân tích |
| Cluster | Job clustering, poll status |
| Volume | Batch volume (API ngoài hoặc ước lượng) |
| Export | Excel, Google Sheets |

## Config

```env
KEYWORD_VOLUME_API_URL=...   # tùy chọn — không có thì ước lượng
```

## Celery (tùy chọn)

- `app/workers/keyword_tasks.py`
- `app/queue/celery_app.py` + Redis

## Trạng thái

**Khá đầy đủ** — volume phụ thuộc API bên ngoài.

## Liên kết

- [docs/serp_intelligence_layer.md](../serp_intelligence_layer.md)
- [05-content-ai.md](./05-content-ai.md) (dùng KW cho bài viết)
