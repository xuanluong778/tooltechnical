from pydantic import BaseModel, Field


class GscSearchAnalyticsRequest(BaseModel):
    site_url: str = Field(
        ...,
        description="URL property trong GSC, vd https://www.example.com/ hoặc sc-domain:example.com",
    )
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    dimensions: list[str] | None = Field(
        default=None,
        description="Mặc định ['query','page']",
    )
    row_limit: int = Field(default=250, ge=1, le=25000)


class Ga4RunReportRequest(BaseModel):
    property_id: str = Field(
        ...,
        description="ID GA4 (số) hoặc chuỗi properties/123",
    )
    start_date: str = Field(default="7daysAgo")
    end_date: str = Field(default="today")
    metrics: list[str] = Field(
        default_factory=lambda: ["sessions", "activeUsers", "screenPageViews"],
    )
    dimensions: list[str] | None = Field(
        default=None,
        description="Ví dụ ['date'], ['pagePath']",
    )


class GoogleStartResponse(BaseModel):
    auth_url: str
    configured: bool = True


class GoogleStatusResponse(BaseModel):
    connected: bool
    configured: bool
