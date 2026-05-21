# Prompt 3 — Service Layer SaaS Phase 1

Tiếp tục Phase 1 SaaS, chỉ tạo service layer, chưa gắn vào Content AI hoặc Keyword.

## File cần tạo

```txt
app/services/plan_service.py
app/services/subscription_service.py
app/services/usage_tracking_service.py
app/services/entitlement_service.py
app/schemas/saas.py
```

## Yêu cầu chi tiết

## 1. plan_service.py

Tạo các hàm:

```python
list_active_plans(db, public_only=True)
get_plan_by_slug(db, slug)
get_plan_by_id(db, plan_id)
get_limits_for_plan(db, plan_id)
```

Mục tiêu:

- Đọc danh sách gói.
- Lấy gói theo slug/id.
- Lấy quota theo plan.

## 2. subscription_service.py

Tạo các hàm:

```python
get_active_subscription(db, user_id)
create_subscription(db, user_id, plan_id, months=1, source="manual", notes=None)
expire_subscription(db, subscription_id)
user_plan_snapshot(db, user_id)
```

Yêu cầu nghiệp vụ:

Khi tạo subscription mới có status `active` hoặc `trialing` cho user:

```txt
Phải đóng subscription cũ còn hiệu lực của cùng user.
Set status = expired
Set ended_at = now()
```

Subscription active hợp lệ khi:

```txt
status IN ("trialing", "active")
current_period_end > now()
ended_at IS NULL hoặc ended_at > now()
```

## 3. usage_tracking_service.py

Tạo các hàm:

```python
get_monthly_usage(db, user_id, feature_key, month=None)
get_quota_remaining(db, user_id, feature_key, plan_id=None)
record_successful_usage(
    db,
    user_id,
    feature_key,
    quantity=1,
    subscription_id=None,
    plan_id=None,
    idempotency_key=None,
    metadata=None
)
```

`record_successful_usage` phải:

```txt
1. Insert usage_events
2. Upsert monthly_usage
3. Cộng quantity_used
4. Cộng credits_used nếu có truyền
5. Chống ghi trùng bằng idempotency_key nếu có
6. Chỉ dùng để ghi khi tác vụ thành công
```

Không được ghi usage khi tác vụ fail.

## 4. entitlement_service.py

Tạo các hàm:

```python
is_saas_enforcement_enabled()
check_feature(db, user, feature_key, quantity=1)
assert_feature_allowed(db, user, feature_key, quantity=1)
resolve_effective_plan(db, user)
```

Khi:

```txt
SAAS_ENFORCEMENT=0
```

thì:

```txt
Không chặn user
Trả allowed=True
reason_code="legacy_enforcement_off"
Không ghi usage bắt buộc
Không đổi hành vi app cũ
```

Khi:

```txt
SAAS_ENFORCEMENT=1
```

áp dụng thứ tự quyền:

```txt
1. Admin -> allow full
2. Active subscription + còn quota feature -> allow
3. api_access_enabled = true -> allow theo legacy
4. Trial còn hạn -> allow theo legacy
5. Credit đủ nếu CREDITS_ENABLED=1 -> allow + consume credit theo logic cũ
6. Không đủ -> deny
```

## 5. app/schemas/saas.py

Tạo Pydantic schema cho:

```python
EntitlementResult
PlanResponse
UsageLimitResponse
SubscriptionResponse
UserPlanSnapshot
GrantSubscriptionRequest
RecordUsageRequest
```

`EntitlementResult` cần có:

```python
allowed: bool
reason_code: str
message: str
plan_slug: str | None
subscription_id: int | None
quota_remaining: int | None
feature_key: str
```

## 6. Không sửa các file sau

```txt
app/routers/pages.py
app/routers/analyze.py
app/routers/keywords.py
app/services/trial_access.py
app/services/credits.py
```

## 7. Không thay đổi hành vi app hiện tại

Phase 1 chỉ tạo service, chưa gắn vào luồng sản phẩm thật.

## Sau khi xong, báo cáo

Báo cáo rõ:

- File đã tạo.
- Hàm đã có.
- Enforcement off có đảm bảo không chặn user không.
- Có sửa luồng Content AI / Keyword / Technical không.
