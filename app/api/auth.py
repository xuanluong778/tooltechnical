from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.credit_ledger import CreditLedger
from app.models.user import User
from app.schemas.auth import (
    CreditGrantRequest,
    CreditGrantResult,
    CreditLedgerListResponse,
    CreditLedgerRow,
    CreditPackagesResponse,
    CreditPackagePublic,
    CreditsConfigResponse,
    MessageResponse,
    OtpSendRequest,
    OtpVerifyRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.admin_auth import ensure_admin_user_fields, is_configured_admin_email, skips_otp_for_user
from app.services.auth import get_current_user, get_optional_current_user, login_user, register_user
from app.services.rbac import normalize_role
from app.services.security_audit_log import log_audit_event
from app.services.credits import admin_grant_secret, credits_enforced, grant_credits, public_credit_packages
from app.services.otp_flow import send_login_otp, verify_login_otp


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=MessageResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> MessageResponse:
    register_user(payload, db)
    return MessageResponse(message="Đăng ký thành công. Bạn có thể đăng nhập bằng email và mật khẩu.")


@router.get("/login/flags")
def login_flags(email: str = Query(..., min_length=3), db: Session = Depends(get_db)) -> dict:
    """UI: ẩn OTP khi email là admin (role admin hoặc ADMIN_EMAIL trong env.local)."""
    email_norm = email.strip().lower()
    user = db.query(User).filter(User.email == email_norm).first()
    skip = skips_otp_for_user(user, email_norm)
    return {
        "skip_otp": skip,
        "is_admin": bool(user and str(getattr(user, "role", "") or "").lower() == "admin"),
    }


@router.post("/login", response_model=TokenResponse)
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    token = login_user(payload.email, payload.password, db, payload.otp)
    from app.services.auth import user_from_token

    user = user_from_token(db, token.access_token)
    log_audit_event(action="login", user_id=user.id, resource_type="user", resource_id=str(user.id), request=request)
    return token


@router.post("/otp/send", response_model=MessageResponse)
def otp_send(payload: OtpSendRequest, db: Session = Depends(get_db)) -> MessageResponse:
    send_login_otp(payload.email, db)
    return MessageResponse(message="Đã gửi OTP tới email của bạn (kiểm tra cả thư mục spam).")


@router.post("/otp/verify", response_model=TokenResponse)
def otp_verify(request: Request, payload: OtpVerifyRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token = verify_login_otp(payload.email, payload.otp, db)
    from app.services.auth import user_from_token

    user = user_from_token(db, token.access_token)
    log_audit_event(action="login", user_id=user.id, resource_type="user", resource_id=str(user.id), request=request)
    return token


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserResponse:
    if is_configured_admin_email(current_user.email) and normalize_role(current_user.role) != "admin":
        ensure_admin_user_fields(current_user)
        db.commit()
        db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.get("/credits/config", response_model=CreditsConfigResponse)
def credits_config() -> CreditsConfigResponse:
    return CreditsConfigResponse(enabled=credits_enforced())


_PACKAGES_FOOTNOTE = (
    "Kích hoạt trừ credit: bật CREDITS_ENABLED=1. Admin cộng credit: POST /auth/credits/admin/grant "
    "(header X-Credits-Admin-Key). Thanh toán online có thể tích hợp sau."
)


@router.get("/credits/packages", response_model=CreditPackagesResponse)
def credits_packages(user: User | None = Depends(get_optional_current_user)) -> CreditPackagesResponse:
    rows = public_credit_packages()
    packages = [CreditPackagePublic.model_validate(x) for x in rows]
    bal = int(user.credit_balance) if user else None
    return CreditPackagesResponse(
        credits_system_enabled=credits_enforced(),
        your_balance=bal,
        packages=packages,
        footnote=_PACKAGES_FOOTNOTE,
    )


@router.get("/credits/ledger", response_model=CreditLedgerListResponse)
def credits_ledger(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 100,
) -> CreditLedgerListResponse:
    lim = max(1, min(500, limit))
    rows = (
        db.query(CreditLedger)
        .filter(CreditLedger.user_id == current_user.id)
        .order_by(desc(CreditLedger.id))
        .limit(lim)
        .all()
    )
    return CreditLedgerListResponse(items=[CreditLedgerRow.model_validate(r) for r in rows])


@router.post("/credits/admin/grant", response_model=CreditGrantResult)
def credits_admin_grant(
    payload: CreditGrantRequest,
    db: Session = Depends(get_db),
    x_credits_admin_key: str | None = Header(default=None, alias="X-Credits-Admin-Key"),
) -> CreditGrantResult:
    secret = admin_grant_secret()
    if not secret or (x_credits_admin_key or "").strip() != secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    email = str(payload.email).strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy user.")
    grant_credits(db, user_id=user.id, amount=int(payload.amount), reason="admin_grant", note=None)
    db.commit()
    db.refresh(user)
    return CreditGrantResult(email=user.email, new_balance=int(user.credit_balance or 0))
