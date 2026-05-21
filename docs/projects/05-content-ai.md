# 05 — Content AI

## URL

`GET /content-ai`

## Mục tiêu

Viết bài SEO bằng LLM, chỉnh sửa TinyMCE, post-process (blockquote), ảnh, internal link, xuất bản WordPress/Haravan, bulk theo danh sách từ khóa.

## File chính

| Loại | Path |
|------|------|
| Template | `templates/content_ai.html` (file lớn) |
| Router | `app/routers/pages.py` (phần lớn `/content-ai/*`) |
| LLM | `app/services/llm_content_writer.py` |
| Draft | `app/services/content_draft_builder.py` |
| Blockquote | `app/services/content_blockquote_postprocess.py` |
| Bulk | `app/services/content_ai_bulk_*.py`, `content_ai_bulk_worker_loop.py` |
| Projects | `app/services/content_ai_project_store.py` |
| Prompt SEO | `app/services/seo_content_prompt.py`, `content_seo_checklist.py` |

## Tab chính (trong trang)

| Tab | ID / nút | Chức năng |
|-----|----------|-----------|
| **Viết 1 bài** | `tabMainSingle` | Form đầy đủ: KW, title, slug, meta, outline, content, tags |
| **Viết bài theo từ khóa** | `tabMainBulk` | Import file, queue job, poll tiến độ |

## Tính năng Viết 1 bài

- Gợi ý AI: `POST /content-ai/suggest` (+ SSE stream)
- Draft JSON, optimize HTML, article JSON
- **Blockquote tự động:** `POST /content-ai/postprocess-content`
- TinyMCE editor + preview
- Ảnh: upload, crop, Google Images, auto-insert
- Thumbnail (upload / AI)
- Outline đối thủ, refresh outline
- Internal link WP (gợi ý + apply)
- Publish / draft WordPress
- Projects: list, mở, xóa, export CSV/Sheet

## Tính năng Bulk

| Bước | API / UI |
|------|----------|
| Import file | `POST /content-ai/bulk-import/file` |
| Lưu setup | `POST /content-ai/bulk-setup/save` |
| Bắt đầu job | `POST /content-ai/bulk-jobs/start` |
| Theo dõi | `GET /content-ai/bulk-jobs/{job_id}` |
| Worker | `content_ai_bulk_worker_loop` (startup app) |

## API nhóm (không liệt kê hết)

| Nhóm | Ví dụ path |
|------|------------|
| Sinh nội dung | `/content-ai/draft`, `/suggest`, `/optimize-html` |
| Projects | `/content-ai/projects`, `.../export.csv` |
| Ảnh | `/upload-image`, `/google-images/*`, `/auto-insert-images` |
| WP | `/content-ai/wordpress/*`, publish endpoints |
| Haravan | haravan connect trong integrations |
| Knowledge | context từ KB user |

## Env quan trọng

```env
CONTENT_AI_LLM_MODE=auto   # auto | off | title_meta_only | content_only
LLM_PROVIDER=openai
CONTENT_BLOCKQUOTE_ENABLED=1
```

## Quyền truy cập

- Cần JWT
- Trial hoặc **API access** (admin cấp) — xem [10-auth-permissions.md](./10-auth-permissions.md)

## Trạng thái

**Module lớn nhất — đang phát triển tích cực**

## Liên kết

- [08-settings.md](./08-settings.md) (API keys, Publishing, AI KB)
- [12-internal-links.md](./12-internal-links.md)
- [10-auth-permissions.md](./10-auth-permissions.md)
