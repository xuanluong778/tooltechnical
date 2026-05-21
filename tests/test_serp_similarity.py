"""SERP similarity: URL Jaccard + domain-damped overlap."""

from app.services.serp_similarity import compute_serp_similarity, _domain_damped_minmax, _url_jaccard


def test_jaccard_identical():
    urls = ["https://a.com/x", "https://b.com/y"]
    s = compute_serp_similarity({"serp_urls": urls}, {"serp_urls": list(urls)})
    assert s == 1.0


def test_domain_damp_reduces_mega_domain_weight():
    """Nhiều URL cùng domain một phía vs ít URL cùng domain phía kia → điểm domain < 1 dù cùng domain."""
    a = [f"https://bigshop.com/p{i}" for i in range(10)]
    b = ["https://bigshop.com/p0", "https://other.org/1", "https://other.org/2"]
    d = _domain_damped_minmax(a, b)
    assert d < 1.0
    assert d > 0.0


def test_blend_url_weight_monkeypatch(monkeypatch):
    monkeypatch.setenv("SERP_SIM_URL_WEIGHT", "1.0")
    a = ["https://x.com/a", "https://y.com/b"]
    b = ["https://x.com/a", "https://z.com/c"]
    s_full_url = compute_serp_similarity({"serp_urls": a}, {"serp_urls": b})
    assert 0.15 < s_full_url < 0.95


def test_zero_when_either_empty():
    assert compute_serp_similarity({"serp_urls": []}, {"serp_urls": ["https://a.com"]}) == 0.0
