# 13 — Hạ tầng dùng chung

## Static & theme

| File | Vai trò |
|------|---------|
| `static/css/digiseo-theme.css` | Theme sáng/tối |
| `static/css/digiseo-nav.css` | Top nav, dropdown |
| `static/js/digiseo-theme-boot.js` | Áp theme từ settings |
| `static/js/digiseo-i18n.js` | i18n vi/en |
| `static/js/digiseo-admin-nav.js` | Ẩn/hiện link Admin |
| `static/js/digiseo-nav-auth.js` | Login state, modal |

## Partials Jinja

| Partial | Dùng cho |
|---------|----------|
| `digiseo_theme_head.html` | CSS/JS head |
| `digiseo_auth_modal.html` | Modal login/register |
| `digiseo_i18n.html` | i18n + chatbot |
| `digiseo_chatbot.html` | Widget chat |

## Workers & queue

| Component | File |
|-----------|------|
| Celery app | `app/queue/celery_app.py` |
| Keyword tasks | `app/workers/keyword_tasks.py` |
| Crawl worker | `app/workers/crawl_worker.py` |
| Content AI bulk loop | `app/services/content_ai_bulk_worker_loop.py` |
| Crawl scheduler | `app/queue/crawl_scheduler.py` |

## SEO pipeline (technical crawl)

```
app/seo_pipeline/
  crawler_layer.py
  normalize_layer.py
  ranking_pipeline.py
  formatter.py
```

## SERP / intelligence (docs riêng)

- `app/routers/serp_intel.py`
- [../serp_intelligence_layer.md](../serp_intelligence_layer.md)
- [../search_behavior_layer.md](../search_behavior_layer.md)
- [../topical_authority_layer.md](../topical_authority_layer.md)

## WP bulk update

- Router: `app/routers/wp_bulk_update.py`
- Service: `app/services/wp_bulk_update.py`

## User files

- `app/routers/user_files.py` — upload file theo user scope

## Tests

```bash
.venv\Scripts\python.exe -m pytest tests/
```

Ví dụ: `tests/test_content_blockquote_postprocess.py`

## Health

`GET /health` — `main.py`

## Swagger

`GET /docs` — FastAPI auto OpenAPI

## Liên kết

- [00-overview-stack.md](./00-overview-stack.md)
- [README.md](./README.md)
