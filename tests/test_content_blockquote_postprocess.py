"""Blockquote auto-insert post-process."""

from app.services.content_blockquote_postprocess import (
    postprocess_content_blockquotes,
    target_blockquote_count,
)


def _sample_article(paragraphs: int = 12, words_per_para: int = 55) -> str:
    chunks = []
    chunks.append("<h1>Tiêu đề bài viết SEO</h1>")
    for i in range(paragraphs):
        w = " ".join([f"từ{i}{j}" for j in range(words_per_para)])
        chunks.append(f"<p>Đoạn {i + 1}: {w}.</p>")
    chunks.append("<h2>FAQ</h2><p>Câu hỏi ngắn?</p>")
    return "\n".join(chunks)


def test_target_count_by_words():
    assert target_blockquote_count(500, rng=__import__("random").Random(1)) == 1
    assert target_blockquote_count(1200, rng=__import__("random").Random(1)) == 2
    assert target_blockquote_count(1700, rng=__import__("random").Random(1)) == 3
    assert target_blockquote_count(2500, rng=__import__("random").Random(1)) in (3, 4)


def test_inserts_blockquotes_evenly():
    html = _sample_article(paragraphs=14, words_per_para=60)
    out = postprocess_content_blockquotes(html, seed=42)
    assert out.count("<blockquote>") >= 1
    assert out.count("<blockquote>") <= 4
    assert "<blockquote><p>" in out


def test_skips_faq_and_short_paragraphs():
    html = """
    <h1>Tiêu đề</h1>
    <p>""" + " ".join(["word"] * 50) + """</p>
    <h2>FAQ</h2>
    <p>""" + " ".join(["faqword"] * 50) + """</p>
    """
    out = postprocess_content_blockquotes(html, seed=1)
    # FAQ paragraph should not get a blockquote immediately after it in FAQ zone
    faq_pos = out.lower().find("faq")
    if faq_pos >= 0:
        tail = out[faq_pos:]
        assert tail.count("<blockquote>") == 0 or "<blockquote>" not in tail[:200]


def test_respects_existing_blockquotes():
    html = _sample_article(10, 50)
    html += '<blockquote><p>Đã có sẵn.</p></blockquote>'
    out = postprocess_content_blockquotes(html, seed=99)
    assert out.count("<blockquote>") <= 4


def test_no_consecutive_blockquotes():
    html = _sample_article(16, 65)
    out = postprocess_content_blockquotes(html, seed=7)
    assert "</blockquote><blockquote>" not in out.replace(" ", "")
    assert "</blockquote>\n<blockquote>" not in out
