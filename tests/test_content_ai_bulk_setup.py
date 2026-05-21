"""Bulk setup draft projects (tab Lưu nháp)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.content_ai_project_store import (
    PROJECT_FILE,
    _project_list_row,
    find_project_by_site_keyword,
    save_or_update_written_bulk_project,
    upsert_bulk_setup_projects,
)


@pytest.fixture
def isolated_projects(tmp_path, monkeypatch):
    p = tmp_path / "content_ai_projects.json"
    monkeypatch.setattr("app.services.content_ai_project_store.PROJECT_FILE", p)
    p.write_text("[]", encoding="utf-8")
    return p


def test_upsert_bulk_setup_creates_setup_draft(isolated_projects):
    saved = upsert_bulk_setup_projects(
        user_id=1,
        target_website="https://itsieuviet.com",
        items=[
            {
                "keyword": "sửa máy tính quận 5",
                "custom_title": "Tiêu đề nháp",
                "custom_description": "Meta nháp",
                "custom_outline": "## H2\n### H3",
            }
        ],
    )
    assert len(saved) == 1
    assert saved[0]["action"] == "created"
    data = json.loads(isolated_projects.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["origin"] == "bulk_setup"
    assert data[0]["content"] == ""
    row = _project_list_row(data[0])
    assert row["is_setup_draft"] is True
    assert row["status"] == "setup_draft"


def test_written_bulk_updates_setup_to_ready(isolated_projects):
    upsert_bulk_setup_projects(
        user_id=1,
        target_website="https://www.itsieuviet.com",
        items=[{"keyword": "cài win tại nhà", "custom_outline": "## A"}],
    )
    existing = find_project_by_site_keyword(1, "itsieuviet.com", "cài win tại nhà")
    assert existing is not None
    source = {
        "title": "Cài win",
        "content": "<p>Nội dung đầy đủ</p>",
        "slug": "cai-win",
        "tags": [],
        "meta_description": "Meta",
        "target_website": "https://itsieuviet.com",
        "primary_keyword": "cài win tại nhà",
        "secondary_keywords": [],
        "outline_content": "## A",
    }
    draft = {**source, "content": source["content"]}
    pid = save_or_update_written_bulk_project(user_id=1, source_payload=source, draft_payload=draft)
    assert pid == existing["id"]
    data = json.loads(isolated_projects.read_text(encoding="utf-8"))
    row = _project_list_row(data[0])
    assert row["is_setup_draft"] is False
    assert row["status"] == "ready"
    assert row["word_count"] > 0
