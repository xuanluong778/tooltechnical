from app.services.structured_parser import parse_structured_html


def test_parse_structured_basic() -> None:
    html = """<!DOCTYPE html><html lang="en"><head>
    <title>  Hello &amp; World  </title>
    <meta name="description" content="  Desc  ">
    <link rel="canonical" href="/path/">
    <meta name="robots" content="index, follow">
    </head><body>
    <h1> Main </h1><h1>Second</h1>
    <h2>Sub</h2>
    <img src="a.png" alt="ok"><img src="b.png">
    <p>word "one two" three</p>
    </body></html>"""
    base = "https://example.com/foo/"
    p = parse_structured_html(html, base)
    assert p["title"] == "Hello & World"
    assert p["meta_description"] == "Desc"
    assert p["canonical"].startswith("https://example.com")
    assert p["h1_count"] == 2
    assert len(p["h2"]) >= 1
    assert p["images_missing_alt"] == 1
    assert "noindex" not in (p.get("robots_meta") or "").lower()


def test_parse_structured_ignores_decorative_missing_alt() -> None:
    html = """<html><head><title>X</title></head><body>
    <img src="icon.png" class="icon" width="24" height="24">
    <img src="hero.jpg" width="800" height="400">
    </body></html>"""
    p = parse_structured_html(html, "https://example.com/")
    assert p["images_total"] == 2
    # decorative icon excluded; only hero without alt counted
    assert p["images_missing_alt"] == 1
