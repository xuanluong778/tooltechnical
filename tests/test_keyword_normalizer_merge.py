from app.services.keyword_normalizer import clustering_signature, merge_similar_keyword_records
from app.services.serp_fetcher import is_serp_noise_or_ad_url


def test_clustering_signature_stem_plural():
    a = clustering_signature("Running shoes for sale")
    b = clustering_signature("running shoe sale")
    assert a == b


def test_merge_similar_merges_variants():
    rows = [
        {"keyword": "blue widget", "source": "user"},
        {"keyword": "Blue widgets", "source": "gsc", "url": "https://ex.com/p1"},
    ]
    out = merge_similar_keyword_records(rows)
    assert len(out) == 1
    assert out[0].get("gsc_primary_url") or out[0].get("gsc_landing_urls")


def test_is_serp_noise_or_ad_url():
    assert is_serp_noise_or_ad_url("https://googleadservices.com/pagead/aclk?sa=l&ai=1")
    assert not is_serp_noise_or_ad_url("https://example.com/blog/post")
