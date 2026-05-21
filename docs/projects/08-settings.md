# 08 — Cài đặt (Settings)

## URL

`GET /settings`  
API: `/api/settings/*` — `app/routers/settings_api.py`

## Mục tiêu

Cấu hình tài khoản, API keys, AI provider, Knowledge Base, site xuất bản, GSC, theme/i18n hệ thống.

## File chính

| Loại | Path |
|------|------|
| Template | `templates/settings.html` |
| Router API | `app/routers/settings_api.py` |
| API keys DB | `app/services/user_api_keys_db.py`, `api_keys_store.py` |
| KB | `app/services/ai_knowledge_store.py`, `ai_knowledge_docs.py` |
| Publishing | `app/services/publishing_sites_store.py` |
| WP/Haravan/Shopify | `wp_connect.py`, `webcake_connect.py`, `shopify_connect.py` |
| Google | `google_token_store.py` |

## Sidebar — từng mục (hash URL)

| # | Hash | Mục | Chức năng |
|---|------|-----|-----------|
| 1 | `#account` | Tài khoản | Email, trạng thái, trial |
| 2 | `#affiliate` | Affiliate | Form đăng ký affiliate |
| 3 | `#api-keys` | Khóa API | Thêm/sửa/test key OpenAI, Anthropic… → trial 7 ngày lần đầu |
| 4 | `#ai-provider` | Nhà cung cấp AI | Provider/model mặc định |
| 5 | `#ai-knowledge-base` | AI Knowledge Base | Tạo KB, import, reindex, search |
| 6 | `#publishing` | Xuất bản | WordPress, Haravan, Shopify, Webcake |
| 7 | `#search-console` | Search Console | GSC (**badge PRO**) |
| 8 | `#system` | Hệ thống | Theme sáng/tối, ngôn ngữ vi/en, batch size… |

## Liên kết với module khác

- Content AI đọc **Publishing profiles** và **API keys**
- Report đọc **GSC** khi đã OAuth

## Trạng thái

**Khung UI đầy đủ** — một số mục phụ thuộc cấu hình Google/OAuth.

## Liên kết

- [05-content-ai.md](./05-content-ai.md)
- [10-auth-permissions.md](./10-auth-permissions.md)
