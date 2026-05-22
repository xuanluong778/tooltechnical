# 09 — Quản trị viên (Admin)

## URL

`GET /admin`  
API: `/admin/api/*`, alias `/api/admin/*`

## Ai được xem?

Chỉ user có `role === "admin"` (nav ẩn qua `static/js/digiseo-admin-nav.js` + `data-nav-admin`).

> Không dùng `/auth/login/flags` `is_admin` cho nav — chỉ `/auth/me` role.

## File chính

| Loại | Path |
|------|------|
| Template | `templates/admin.html` |
| Router page | `app/routers/admin.py` |
| API | `app/routers/admin.py` (admin_api) |
| Service | `app/services/admin_service.py` |
| Policy list user | `app/services/user_account_policy.py` (Gmail + ADMIN_EMAIL) |
| Script dọn user test | `scripts/cleanup_junk_users.py` |

## Màn hình chính

### Danh sách user

- Lọc: role, status, trial, segment
- Cột: API on/off, API Admin pool, trial label (**API cấp** vs trial 7 ngày)
- Toggle nhỏ (CSS riêng, không bị `flex:1` của label)

### Chi tiết user — tab

| Tab | `data-tab` | Nội dung |
|-----|------------|----------|
| SEO Projects | `seo` | Dự án quét technical |
| Content AI | `content` | Projects Content AI |
| Knowledge Base | `kb` | KB của user |
| Bulk jobs | `bulk` | Job bulk Content AI |
| API keys | `keys` | Keys đã lưu (masked) |
| Publishing | `pub` | Site xuất bản |
| Audit | `audit` | Security audit log |

### Quyền chỉnh trên user

| Toggle | Field DB | Ý nghĩa |
|--------|----------|---------|
| Cho phép dùng API | `api_access_enabled` | Bật AI/API — bypass trial |
| Dùng API Admin | `use_admin_api_pool` | Dùng key pool `env.local` |
| Role / Status | `role`, `status` | admin, user, editor, viewer… |

## API ví dụ

| Method | Path |
|--------|------|
| GET | `/admin/api/users` |
| PATCH | user role, status, api flags |
| GET | audit logs |

## Trạng thái

**Hoàn chỉnh** cho vận hành nội bộ

## Liên kết

- [10-auth-permissions.md](./10-auth-permissions.md)
- [08-settings.md](./08-settings.md)
