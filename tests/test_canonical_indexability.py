from app.services.canonical_utils import resolve_canonical_signals
from app.services.indexability import assess_indexability


def test_canonical_self_when_absent() -> None:
    html = "<html><head><title>x</title></head><body></body></html>"
    r = resolve_canonical_signals(html, "https://example.com/page")
    assert r["canonical_url"] is None
    assert r["is_canonical_self"] is True
    assert r["canonical_mismatch"] is False
    assert r["final_effective_url"]


def test_canonical_mismatch() -> None:
    html = '<html><head><link rel="canonical" href="https://example.com/other"></head><body></body></html>'
    r = resolve_canonical_signals(html, "https://example.com/page")
    assert r["canonical_url"]
    assert r["canonical_mismatch"] is True
    assert r["is_canonical_self"] is False


def test_indexability_noindex_meta() -> None:
    html = '<html><head><meta name="robots" content="noindex,follow"></head><body></body></html>'
    r = assess_indexability(html, {}, 200, secondary_headers={})
    assert r["indexable"] is False
    assert r["indexability_confidence"] > 0


def test_indexability_http_404() -> None:
    r = assess_indexability("<html></html>", {}, 404, secondary_headers={})
    assert r["indexable"] is False
