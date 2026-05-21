from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    domain: str


class ProjectResponse(BaseModel):
    id: int
    domain: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyzeProjectRequest(BaseModel):
    project_id: int = Field(ge=1)
    url: str


class AnalyzeProjectResponse(BaseModel):
    scan_id: int
    seo_score: int


class ScanListItem(BaseModel):
    id: int
    seo_score: int
    total_pages: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SEOTrendPoint(BaseModel):
    date: str
    seo_score: int


class ScanIssueResponse(BaseModel):
    type: str
    severity: str
    message: str

    model_config = {"from_attributes": True}


class ScanPageResponse(BaseModel):
    id: int
    url: str
    status: int
    title: str
    page_score: int
    issues: list[ScanIssueResponse]

    model_config = {"from_attributes": True}


class ScanDetailResponse(BaseModel):
    id: int
    project_id: int
    seo_score: int
    total_pages: int
    created_at: datetime
    pages: list[ScanPageResponse]
    summary: dict


class PaginatedScansResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[ScanListItem]


class PaginatedScanPagesResponse(BaseModel):
    total_pages_count: int
    page_offset: int
    page_limit: int
    items: list[ScanPageResponse]


class ScanDetailPaginatedResponse(BaseModel):
    id: int
    project_id: int
    seo_score: int
    total_pages: int
    created_at: datetime
    pages: PaginatedScanPagesResponse
    summary: dict


class ScanCompareResponse(BaseModel):
    current_scan_id: int
    previous_scan_id: int
    score_diff: int
    issues_fixed: int
    issues_added: int
    pages_improved: int
    pages_declined: int
    message: str | None = None
