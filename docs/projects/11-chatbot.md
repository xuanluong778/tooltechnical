# 11 — Chatbot (toàn site)

## Mục tiêu

Hỗ trợ người dùng qua chat nổi góc phải mọi trang (sau khi include partial).

## File chính

| Loại | Path |
|------|------|
| HTML | `templates/partials/beeseo_chatbot.html` |
| CSS | `static/css/beeseo-chatbot.css` |
| JS | `static/js/beeseo-chatbot.js` |
| Include | `templates/partials/beeseo_i18n.html` |
| Router | `app/routers/chatbot.py` |
| Service | `app/services/chatbot_service.py` |

## API

| Prefix | Path |
|--------|------|
| `/chatbot` | message, history… |
| `/api/chatbot` | alias |

## UI

- Nút avatar góc phải
- Panel: tin nhắn, quick questions, input textarea
- Avatar: `/static/img/beeseo-chatbot-avatar.png`

## Trạng thái

**Có và chạy** — prompt/LLM phụ thuộc API access user.

## Liên kết

- [10-auth-permissions.md](./10-auth-permissions.md)
- [13-shared-infrastructure.md](./13-shared-infrastructure.md)
