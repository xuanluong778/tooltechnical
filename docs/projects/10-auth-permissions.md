# 10 — Auth & Phân quyền

## Router

`app/api/auth.py` — prefix `/auth`

## Đăng ký / đăng nhập

| Flow | Endpoint |
|------|----------|
| Đăng ký | `POST /auth/register` |
| Đăng nhập | `POST /auth/login` (email + password) |
| OTP (đăng ký) | `POST /auth/otp/send`, `/auth/otp/verify` |
| Session | `GET /auth/me` → JWT Bearer |

## Role

| Role | Mô tả |
|------|--------|
| `admin` | Full quyền + tab Admin + coi như API on + API Admin pool |
| `user` | User thường |
| `editor` | RBAC mở rộng |
| `viewer` | Chủ yếu xem |

File: `app/services/rbac.py`, `app/services/admin_auth.py`

## Trial 7 ngày

| File | Vai trò |
|------|---------|
| `app/services/user_trial_service.py` | Snapshot trial cho UI/admin |
| `app/services/trial_access.py` | `require_active_trial` — **bypass** nếu `api_access_enabled` |

Kích hoạt trial: user thêm **API key hợp lệ** lần đầu trong Settings (nếu admin chưa cấp API).

## API access (quan trọng)

| Flag | Ý nghĩa |
|------|---------|
| `api_access_enabled` | Admin bật → user dùng AI **không cần** trial |
| `use_admin_api_pool` | Dùng key hệ thống (`env.local`), không bắt buộc key riêng |

Service: `app/services/user_api_access.py`

### Thứ tự ưu tiên LLM key

1. Admin role → pool admin
2. User có `use_admin_api_pool` + API on → pool admin
3. User API key riêng (mã hóa DB)
4. Từ chối nếu không đủ quyền

## Credits (khung)

| Endpoint | Mô tả |
|----------|--------|
| `GET /auth/credits/config` | Cấu hình |
| `GET /auth/credits/packages` | Gói (chưa payment gateway đầy đủ) |
| `GET /auth/credits/ledger` | Sổ credit |
| `POST /auth/credits/admin/grant` | Admin cấp credit |

## Bảo mật

- Mật khẩu: **bcrypt**
- API key user: **cryptography** (`app/core/secrets_crypto.py`)
- Audit: `app/services/security_audit_log.py`

## Env

```env
ADMIN_EMAIL=admin@...
JWT_SECRET=...
SMTP_*=...          # OTP Gmail
```

## Trạng thái

**Auth hoàn chỉnh** — Google OAuth login tùy cấu hình.

## Liên kết

- [01-home-landing.md](./01-home-landing.md)
- [09-admin.md](./09-admin.md)
- [05-content-ai.md](./05-content-ai.md)
