from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("RUN_KEYWORD_INTEL_TEST"),
    reason="Set RUN_KEYWORD_INTEL_TEST=1 to run (uses sklearn stack).",
)


def test_build_keyword_intelligence_minimal() -> None:
    os.environ["KEYWORD_INTENT_MAX_SERP_GT"] = "0"
    os.environ["KEYWORD_INTEL_CLUSTER_FETCH_SERP"] = "0"
    from app.services.keyword_intelligence_api import build_keyword_intelligence_response

    r = build_keyword_intelligence_response(seed_keyword="test query", url="https://example.com")
    assert "keywords" in r and "clusters" in r
    assert isinstance(r["intent_summary"], dict)
