# Prompt 4 — Admin Router Test SaaS Phase 1

Tiếp tục Phase 1 SaaS.

Tạo router admin nhẹ để test SaaS manual.

## File cần tạo

```txt
app/routers/saas_admin.py
```

Sau đó thêm `include_router` vào `main.py`.

## API cần có

## 1. GET /api/admin/saas/plans

Trả danh sách plans + usage limits.

Yêu cầu:

```txt
Chỉ admin được gọi.
Không thay đổi dữ liệu.
```

## 2. GET /api/admin/saas/users/{user_id}/subscription

Trả subscription hiện tại của user nếu có.

Thông tin trả về nên gồm:

```txt
user_id
subscription_id
plan_slug
plan_name
status
current_period_start
current_period_end
cancel_at_period_end
notes
```

Nếu user chưa có subscription SaaS:

```txt
Trả null hoặc message rõ ràng.
Không deny user.
```

## 3. POST /api/admin/saas/users/{user_id}/grant-subscription

Body:

```json
{
  "plan_slug": "pro",
  "months": 1,
  "notes": "Admin grant test"
}
```

Tác dụng:

```txt
Tạo subscription active/manual cho user.
Đóng subscription cũ nếu có.
Không đụng user_trials cũ.
Không đụng credit_balance cũ.
```

## 4. GET /api/admin/saas/users/{user_id}/entitlement-check?feature_key=content_ai_article

Gọi:

```python
entitlement_service.check_feature(...)
```

Trả về `EntitlementResult`.

Yêu cầu:

```txt
Nếu SAAS_ENFORCEMENT=0 thì phải allowed=True, reason_code="legacy_enforcement_off".
Không chặn user.
Không ghi usage.
```

## 5. POST /api/admin/saas/users/{user_id}/usage/test-record

Body:

```json
{
  "feature_key": "content_ai_article",
  "quantity": 1,
  "idempotency_key": "test-user-1-content-ai-001"
}
```

Tác dụng:

```txt
Ghi thử usage_events.
Upsert monthly_usage.
Nếu idempotency_key đã tồn tại thì không ghi trùng.
```

## Bảo mật

Router này chỉ dành cho admin.

Hãy dùng cơ chế admin hiện có trong app, ví dụ:

```txt
current_user.role == "admin"
```

hoặc dependency admin hiện có nếu repo đã có.

Không tự tạo cơ chế auth mới nếu repo đã có sẵn.

## Không được làm

```txt
Không gắn router này vào Content AI
Không gắn quota vào Keyword Research
Không gắn quota vào Technical Audit
Không bật SAAS_ENFORCEMENT mặc định
Không làm payment thật
Không sửa UI lớn
Không chặn user thường khi họ dùng app cũ
```

## Sau khi xong, báo cáo

Báo cáo rõ:

- Endpoint đã tạo.
- Cách test từng endpoint.
- File nào đã sửa.
- Có ảnh hưởng hệ thống cũ không.
- SAAS_ENFORCEMENT hiện đang mặc định là gì.
