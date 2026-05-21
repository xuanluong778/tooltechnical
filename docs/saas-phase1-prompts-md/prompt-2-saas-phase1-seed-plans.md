# Prompt 2 — Seed Plans + Usage Limits SaaS Phase 1

Tiếp tục Phase 1 SaaS.

Hãy tạo script seed dữ liệu gói SaaS.

## File cần tạo

```txt
scripts/seed_saas_plans.py
```

## Yêu cầu

### 1. Seed 4 plans

Tạo 4 gói:

```txt
free_trial
starter
pro
agency
```

Thông tin cơ bản gợi ý:

```txt
free_trial:
- name: Free Trial
- price_amount: 0
- currency: VND
- billing_cycle: none
- is_active: true
- is_public: true
- sort_order: 1

starter:
- name: Starter
- price_amount: 199000
- currency: VND
- billing_cycle: monthly
- is_active: true
- is_public: true
- sort_order: 2

pro:
- name: Pro
- price_amount: 499000
- currency: VND
- billing_cycle: monthly
- is_active: true
- is_public: true
- sort_order: 3

agency:
- name: Agency
- price_amount: 1499000
- currency: VND
- billing_cycle: monthly
- is_active: true
- is_public: true
- sort_order: 4
```

### 2. Seed usage_limits cơ bản

Seed các giới hạn sau:

```txt
free_trial: content_ai_article = 3 monthly
free_trial: technical_audit = 3 monthly
free_trial: keyword_research = 50 monthly
free_trial: content_ai_bulk_article = 0 monthly

starter: content_ai_article = 30 monthly
pro: content_ai_article = 150 monthly
agency: content_ai_article = -1 monthly
```

Quy ước:

```txt
limit_value = -1 nghĩa là không giới hạn
limit_value = 0 và is_hard_limit = true nghĩa là cấm dùng
```

### 3. Script phải idempotent

Script phải chạy được nhiều lần mà không tạo trùng dữ liệu.

Nếu plan đã tồn tại:

```txt
Update name, price_amount, currency, billing_cycle, is_active, is_public, sort_order nếu cần.
```

Nếu usage_limit đã tồn tại:

```txt
Update limit_value, period, is_hard_limit nếu cần.
```

### 4. Không thay đổi hành vi app cũ

Không được:

```txt
Không bật SAAS_ENFORCEMENT
Không gắn quota vào Content AI
Không gắn quota vào Keyword Research
Không sửa trial_access.py
Không sửa credits.py
Không chặn user
```

### 5. Sau khi làm xong, báo cáo

Báo cáo rõ:

- File đã tạo.
- Dữ liệu seed gồm những gì.
- Lệnh chạy script theo cấu trúc repo hiện tại.
- Cách kiểm tra trong database.
- Xác nhận không thay đổi hành vi app cũ.
