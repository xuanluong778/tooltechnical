"""Schema generator pipeline smoke tests."""

from __future__ import annotations

from app.services.schema_api import build_schema_generator_response


def test_schema_generator_html_product_signals() -> None:
    r = build_schema_generator_response(
        html="<html><title>X</title><body><h1>Item</h1>price 9.99 add to cart</body></html>",
        url="https://shop.example/p/1",
        fetch_serp_flag=False,
    )
    assert r["ok"] is True
    types = {n.get("@type") for n in r["schemas"]}
    assert "Product" in types
    assert r["primary_schema"].get("@type") == "Product"
    assert "validation" in r
    assert "serp_alignment" in r


def test_schema_generator_faq_heading() -> None:
    r = build_schema_generator_response(
        html="<html><body><h2>Question one?</h2><p>Answer one.</p></body></html>",
        url="https://ex.com/faq",
        fetch_serp_flag=False,
    )
    assert r["ok"] is True
    faq = next((s for s in r["schemas"] if s.get("@type") == "FAQPage"), None)
    assert faq is not None
    assert isinstance(faq.get("mainEntity"), list)
    assert len(faq["mainEntity"]) >= 1
