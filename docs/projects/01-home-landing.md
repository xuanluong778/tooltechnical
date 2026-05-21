# 01 — Trang chủ (Landing)

## URL

`GET /`

## Mục tiêu

Trang marketing + cổng vào app: giới thiệu tính năng, đăng nhập/đăng ký, chuyển sang công cụ sau khi có JWT.

## File chính

| Loại | Path |
|------|------|
| Template | `templates/home.html` |
| Auth modal | `templates/partials/beeseo_auth_modal.html` |
| JS auth | `static/js/beeseo-nav-auth.js` |
| Theme / i18n | `templates/partials/beeseo_theme_head.html`, `static/js/beeseo-i18n.js` |

## Tab / UI trong modal đăng nhập

| Tab | Chức năng |
|-----|-----------|
| **Đăng nhập** | Email + mật khẩu → `POST /auth/login` |
| **Đăng ký** | Gmail + OTP (`POST /auth/otp/send`, `/auth/otp/verify`) + mật khẩu |

> OTP **chỉ** ở tab Đăng ký (đã bỏ khối OTP khỏi tab Đăng nhập).

## API liên quan

| Method | Path |
|--------|------|
| POST | `/auth/register` |
| POST | `/auth/login` |
| POST | `/auth/otp/send`, `/auth/otp/verify` |
| GET | `/auth/me` |
| GET | `/auth/login/flags` |

## Trạng thái

**Hoàn chỉnh** — Google OAuth trên UI thường hiển thị “chưa cấu hình” nếu thiếu client ID trong env.

## Liên kết

- [10-auth-permissions.md](./10-auth-permissions.md)
- [README.md](./README.md)
