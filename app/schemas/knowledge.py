"""Pydantic schemas for Knowledge Base API (future use)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ScopeType = Literal["global", "user", "project"]
KnowledgeStatus = Literal["active", "draft", "archived"]
ItemType = Literal["snippet", "brand_profile", "faq", "product", "policy", "document"]
ContentFormat = Literal["text", "markdown", "html"]
VersionEntityType = Literal["knowledge_base", "knowledge_category", "knowledge_item"]


class KnowledgeBaseBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=128)
    description: str | None = None
    brand_name: str | None = Field(default=None, max_length=255)
    website_url: str | None = Field(default=None, max_length=512)
    tone: str | None = Field(default="professional", max_length=32)
    language: str | None = Field(default="vi", max_length=16)
    products_services: str | None = None
    target_audience: str | None = None
    key_facts: str | None = None
    avoid_topics: str | None = None
    custom_instructions: str | None = None
    status: KnowledgeStatus = "active"
    is_default: bool = False


class KnowledgeBaseCreate(KnowledgeBaseBase):
    scope_type: ScopeType = "user"
    project_id: int | None = None


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = None
    description: str | None = None
    brand_name: str | None = None
    website_url: str | None = None
    tone: str | None = None
    language: str | None = None
    products_services: str | None = None
    target_audience: str | None = None
    key_facts: str | None = None
    avoid_topics: str | None = None
    custom_instructions: str | None = None
    status: KnowledgeStatus | None = None
    is_default: bool | None = None


class KnowledgeBaseResponse(KnowledgeBaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scope_type: ScopeType
    user_id: int | None
    project_id: int | None
    created_at: datetime
    updated_at: datetime


class KnowledgeCategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=128)
    description: str | None = None
    parent_id: int | None = None
    sort_order: int = 0
    status: KnowledgeStatus = "active"


class KnowledgeCategoryCreate(KnowledgeCategoryBase):
    knowledge_base_id: int


class KnowledgeCategoryResponse(KnowledgeCategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    knowledge_base_id: int
    created_at: datetime
    updated_at: datetime


class KnowledgeItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    content: str = ""
    content_format: ContentFormat = "markdown"
    item_type: ItemType = "snippet"
    category_id: int | None = None
    source_url: str | None = Field(default=None, max_length=1024)
    metadata_json: str | None = None
    status: KnowledgeStatus = "active"
    sort_order: int = 0


class KnowledgeItemCreate(KnowledgeItemBase):
    knowledge_base_id: int


class KnowledgeItemResponse(KnowledgeItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    knowledge_base_id: int
    created_by_user_id: int | None
    created_at: datetime
    updated_at: datetime


class KnowledgeEmbeddingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    knowledge_item_id: int
    chunk_index: int
    chunk_text: str
    embedding_model: str
    embedding_dim: int
    content_hash: str | None
    created_at: datetime


class KnowledgeVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: VersionEntityType
    entity_id: int
    version_number: int
    changed_by_user_id: int | None
    change_note: str | None
    created_at: datetime
