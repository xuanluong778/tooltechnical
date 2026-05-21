# 02 — Dashboard (Báo cáo Technical)

## URL

`GET /report`

## Mục tiêu

Xem tổng hợp kết quả quét Technical SEO: checklist theo nhóm lỗi, lịch sử audit, export, action plan, GSC (nếu đã kết nối).

## File chính

| Loại | Path |
|------|------|
| Template | `templates/report.html` |
| Router API | `app/routers/report.py` |
| Báo cáo | `app/services/report_builder.py` |

## UI

- **Sidebar trái:** nhóm checklist / icon theo loại issue (broken link, robots, sitemap, meta…)
- **Nội dung:** audit mới nhất, danh sách run, chi tiết từng audit
- Không có tab con — một layout báo cáo thống nhất

## API chính

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/report` | Trang HTML |
| GET | `/api/audit/latest` | Audit mới nhất |
| GET | `/api/audit/runs` | Lịch sử quét |
| GET | `/api/audit/mine` | Audit của user |
| GET | `/api/audit/{id}` | Chi tiết |
| GET | `/api/audit/{id}/export.csv` | CSV |
| GET | `/api/audit/{id}/export.pdf` | PDF |
| GET | `/api/audit/{id}/export.gsheet` | Google Sheet |
| GET | `/api/report`, `/api/report.csv`, `/api/report.pdf` | Báo cáo tổng |
| GET | `/api/action-plan` | Kế hoạch xử lý |
| GET | `/api/gsc-indexing-counts` | Số liệu indexing GSC |

## Luồng dữ liệu

```
/tool quét URL → lưu project/audit → /report đọc API audit
```

## Trạng thái

**Hoàn chỉnh** — gắn chặt module [03-technical-seo-tool.md](./03-technical-seo-tool.md).

## Liên kết

- [03-technical-seo-tool.md](./03-technical-seo-tool.md)
- [08-settings.md](./08-settings.md) (Search Console)
