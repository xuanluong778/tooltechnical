from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.password_policy import validate_password_strength


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    otp: str = Field(min_length=4, max_length=12)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return validate_password_strength(v)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    otp: str | None = Field(default=None, min_length=4, max_length=12)

    @field_validator("otp", mode="before")
    @classmethod
    def normalize_otp(cls, v: object) -> str | None:
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            v = str(v)
        s = v.strip().replace(" ", "")
        return s if s else None

    @model_validator(mode="after")
    def password_strength_when_otp(self) -> "UserLogin":
        if self.otp:
            validate_password_strength(self.password)
        return self


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    credit_balance: int = 0
    role: str = "user"
    status: str = "active"
    api_access_enabled: bool = False
    use_admin_api_pool: bool = False

    model_config = {"from_attributes": True}


class CreditGrantRequest(BaseModel):
    email: EmailStr
    amount: int = Field(gt=0, le=1_000_000)


class CreditsConfigResponse(BaseModel):
    enabled: bool


class CreditPackagePublic(BaseModel):
    id: str
    name: str
    credits: int = 0
    description: str = ""
    price_hint: str | None = None


class CreditPackagesResponse(BaseModel):
    credits_system_enabled: bool
    your_balance: int | None = None
    packages: list[CreditPackagePublic]
    footnote: str = ""


class CreditLedgerRow(BaseModel):
    id: int
    delta: int
    balance_after: int
    reason: str
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CreditGrantResult(BaseModel):
    ok: bool = True
    email: EmailStr
    new_balance: int


class CreditLedgerListResponse(BaseModel):
    items: list[CreditLedgerRow]


class MessageResponse(BaseModel):
    message: str


class OtpSendRequest(BaseModel):
    email: EmailStr


class OtpVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=4, max_length=12)
