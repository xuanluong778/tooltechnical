# Phase 1 — SaaS Schema Design

Tài liệu tham chiếu cho models Phase 1. **Chưa** bật enforcement; **chưa** seed plans.

## Bảng mới

| Bảng | Model file | Quan hệ users |
|------|------------|---------------|
| `plans` | `app/models/plan.py` | Gián tiếp qua subscriptions |
| `subscriptions` | `app/models/subscription.py` | FK `user_id` → `users.id` |
| `usage_limits` | `app/models/usage_limit.py` | Qua `plan_id` |
| `usage_events` | `app/models/usage_event.py` | FK `user_id` |
| `monthly_usage` | `app/models/monthly_usage.py` | FK `user_id` |
| `payment_transactions` | `app/models/payment_transaction.py` | FK `user_id` |

## Bảng cũ (không đổi Phase 1)

- `users`, `user_trials`, `trial_key_claims`, `credit_ledgers`

## Subscription active (logic tương lai)

`status IN ('trialing', 'active')` và `current_period_end > now()` và chưa `ended_at` (hoặc `ended_at > now()`).

## Feature keys (chuẩn hóa)

`content_ai_article`, `content_ai_bulk_article`, `technical_audit`, `seo_score`, `keyword_research`, `keyword_cluster`, `schema_generate`, `wp_publish`, `image_generate`, `chatbot_message`, `knowledge_base_search`, `wordpress_site`

## Quy tắc ưu tiên (Phase 2+, `SAAS_ENFORCEMENT=1`)

1. Admin → allow  
2. Subscription active + quota  
3. API access enabled (legacy)  
4. Trial còn hạn (legacy)  
5. Credit đủ (legacy)  
6. Deny  

Phase 1: chỉ tạo bảng; `SAAS_ENFORCEMENT=0` mặc định.

## Chi tiết cột

Xem docstring trong từng file `app/models/plan.py`, `subscription.py`, …
