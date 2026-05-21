"""Request/response cho tab chấm điểm SEO 1 URL."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UrlSeoScoreboardRequest(BaseModel):
    url: str = Field(..., min_length=4, description="URL cần chấm điểm (http/https).")
    keyword: str | None = Field(default=None, description="Từ khóa mục tiêu — bật so sánh SERP + opportunity.")
    search_volume: int | None = Field(
        default=None,
        ge=0,
        description="Volume/tháng (tùy chọn) để ước tính traffic khi tối ưu.",
    )
    current_serp_position: int | None = Field(
        default=None,
        ge=1,
        le=101,
        description="Thứ hạng hiện tại trên Google (1 = top), nếu biết — tinh chỉnh CTR & opportunity.",
    )


class UrlSeoScoreboardResponse(BaseModel):
    url: str
    normalized_url: str
    fetch: dict[str, Any]
    scores: dict[str, Any]
    breakdown: dict[str, Any]
    issues: list[dict[str, Any]]
    serp: dict[str, Any] | None
    opportunity: dict[str, Any] | None
    weights: dict[str, float]
    pillar_definitions: dict[str, str] = Field(default_factory=dict)
    page_snapshot: dict[str, Any] = Field(default_factory=dict)
    editorial_checklist: dict[str, Any] = Field(default_factory=dict)
    fifteen_pillar_assessment: dict[str, Any] = Field(default_factory=dict)
    serp_top10_crawl: dict[str, Any] = Field(default_factory=dict)
    optimization_report: dict[str, Any] = Field(default_factory=dict)
    generated_at: str
