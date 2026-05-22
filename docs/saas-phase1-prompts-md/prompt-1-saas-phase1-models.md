# Prompt 1 — Lưu tài liệu + tạo Models SaaS Phase 1

Bạn hãy triển khai Phase 1 SaaS nền móng, chỉ tạo schema/model, chưa thay đổi hành vi app cũ.

## Yêu cầu

### 1. Đọc / tạo tài liệu thiết kế

Đọc tài liệu:

```txt
docs/digiseo_saas/26-phase1-schema-design.md
```

Nếu file chưa tồn tại, hãy tạo file này và lưu nội dung thiết kế Phase 1 SaaS schema vào đó.

### 2. Tạo 6 model SQLAlchemy mới

Tạo các file:

```txt
app/models/plan.py
app/models/subscription.py
app/models/usage_limit.py
app/models/usage_event.py
app/models/monthly_usage.py
app/models/payment_transaction.py
```

Các bảng cần có:

```txt
plans
subscriptions
usage_limits
usage_events
monthly_usage
payment_transactions
```

### 3. Tuân thủ thiết kế

- Không sửa bảng `users`.
- Không xóa `user_trials`.
- Không xóa `credit_ledgers`.
- Không sửa `trial_access.py`.
- Không sửa `pages.py` Content AI.
- Không chặn user.
- Không bật SaaS enforcement.
- Thêm đầy đủ index, unique constraint, foreign key theo thiết kế.

### 4. Import model vào main.py

Import các model mới vào `main.py` trước đoạn:

```python
Base.metadata.create_all(bind=engine)
```

Mục tiêu: khi app restart, `create_all` tự tạo bảng mới.

### 5. Sau khi làm xong, báo cáo

Báo cáo rõ:

- File đã tạo.
- File đã sửa.
- Bảng mới đã sẵn sàng chưa.
- Có thay đổi hành vi user cũ hay không.

## Điều cấm trong Prompt 1

Không làm các việc sau:

```txt
Không tạo quota enforcement
Không gắn vào Content AI
Không gắn vào Keyword Research
Không gắn vào Technical Audit
Không sửa luồng trial cũ
Không sửa luồng credit cũ
Không tạo payment thật
```
