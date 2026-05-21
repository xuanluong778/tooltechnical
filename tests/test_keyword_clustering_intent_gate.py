import os


def test_vi_intent_classifier_transactional_vs_info():
    from app.services.search_intent import classify_search_intent

    assert classify_search_intent("mua iphone 15")["intent"] == "transactional"
    assert classify_search_intent("iphone 15 giá bao nhiêu")["intent"] == "transactional"
    assert classify_search_intent("cách sửa laptop")["intent"] == "informational"
    assert classify_search_intent("hướng dẫn sửa laptop")["intent"] == "informational"
    assert classify_search_intent("iphone 15 review")["intent"] in ("commercial", "informational")


def test_intent_gate_blocks_cross_intent_merge():
    # Force scalable path for this tiny test.
    os.environ["KEYWORD_CLUSTER_SCALABLE_N"] = "2"
    os.environ["KEYWORD_CLUSTER_INTENT_STRICT"] = "1"
    os.environ["SERP_FETCH_ENABLED"] = "0"

    from app.services.keyword_clusterer import cluster_keywords

    recs = [
        {"keyword": "mua iphone 15", "source": "t"},
        {"keyword": "iphone 15 giá bao nhiêu", "source": "t"},
        {"keyword": "cách sửa laptop", "source": "t"},
        {"keyword": "hướng dẫn sửa laptop", "source": "t"},
    ]
    clusters = cluster_keywords(recs, fetch_serp=False)

    # Ensure no cluster mixes transactional and informational.
    for c in clusters:
        intents = {str(r.get("intent") or "") for r in (c.get("keywords") or [])}
        assert len(intents) <= 1


def test_vi_synonym_merge_same_intent():
    # Force scalable path.
    os.environ["KEYWORD_CLUSTER_SCALABLE_N"] = "2"
    os.environ["KEYWORD_CLUSTER_INTENT_STRICT"] = "1"
    os.environ["SERP_FETCH_ENABLED"] = "0"
    os.environ["KW_ENABLE_SYNONYMS"] = "1"

    from app.services.keyword_clusterer import cluster_keywords

    recs = [
        {"keyword": "sửa laptop quận 9", "source": "t"},
        {"keyword": "chữa laptop q9", "source": "t"},
    ]
    clusters = cluster_keywords(recs, fetch_serp=False)
    # Expect they merge into 1 cluster (accuracy-first).
    assert len(clusters) == 1

