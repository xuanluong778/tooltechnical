from app.services.html_compare import summarize_raw_vs_rendered


def test_summarize_identical() -> None:
    h = "<html><head><title>T</title></head><body>x</body></html>"
    s = summarize_raw_vs_rendered(h, h, raw_final_url="https://a.com/", rendered_final_url="https://a.com/")
    assert s["identical"] is True
    assert s["title_match"] is True
    assert s["urls_match"] is True
    assert s["content_length_ratio"] == 1.0
    assert s.get("missing_elements_in_raw") == []
    assert s.get("missing_elements_in_rendered") == []


def test_summarize_different_title() -> None:
    a = "<html><head><title>Old</title></head><body></body></html>"
    b = "<html><head><title>New</title></head><body></body></html>"
    s = summarize_raw_vs_rendered(a, b)
    assert s["identical"] is False
    assert s["title_match"] is False
    assert s["title_raw"] == "Old"
    assert s["title_rendered"] == "New"
