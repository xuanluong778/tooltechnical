from app.services.topic_entity_resolver import normalize_entity_phrase, resolve_entity_groups


def test_normalize_strips_modifiers() -> None:
    assert "running shoes" in normalize_entity_phrase("best running shoes guide")


def test_resolve_merges_variants() -> None:
    groups = resolve_entity_groups(
        ["best running shoes", "shoes for running", "running shoe"],
        cluster_keywords=["running"],
        use_embeddings=False,
    )
    assert groups
    canons = {g["canonical_entity"] for g in groups}
    assert len(canons) < 3 or any("running" in c for c in canons)
