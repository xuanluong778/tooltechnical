import pytest

from app.services.analyzer import normalize_url


@pytest.mark.parametrize(
    "raw_url, expected",
    [
        ("example.com", "https://example.com/"),
        ("http://example.com", "http://example.com/"),
        ("https://Example.COM/path", "https://example.com/path"),
        ("localhost", "https://localhost/"),
    ],
)
def test_normalize_url_valid_cases(raw_url: str, expected: str) -> None:
    assert normalize_url(raw_url) == expected


@pytest.mark.parametrize(
    "raw_url",
    [
        "",
        "   ",
        "abc",
        "http://",
        "ftp://example.com",
    ],
)
def test_normalize_url_invalid_cases(raw_url: str) -> None:
    with pytest.raises(ValueError):
        normalize_url(raw_url)
