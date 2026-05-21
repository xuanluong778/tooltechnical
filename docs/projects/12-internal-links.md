# 12 — Internal Linking

## Mục tiêu

Đồng bộ bài WordPress, embedding, gợi ý và chèn internal link ngữ cảnh vào Content AI.

## File chính

| Loại | Path |
|------|------|
| Router | `app/routers/internal_links.py` |
| Package | `app/services/internal_linking/` |
| | `crawler.py`, `embeddings.py`, `similarity.py` |
| | `anchor_generator.py`, `injector.py`, `tasks.py` |

## API (prefix `/internal-links`)

| Nhóm | Ví dụ |
|------|--------|
| Sync WP | Đồng bộ posts/pages |
| Suggest | Gợi ý link theo nội dung |
| Apply | Chèn link vào HTML bài viết |

## Dùng ở đâu?

- Tab **Content AI** → Viết 1 bài (panel internal link WordPress)

## Công nghệ

- Embedding: **sentence-transformers** (khi bật)
- Similarity: sklearn / cosine

## Trạng thái

**Module phụ — tích hợp Content AI**

## Liên kết

- [05-content-ai.md](./05-content-ai.md)
- [08-settings.md](./08-settings.md) (WordPress publishing)
