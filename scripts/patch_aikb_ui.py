# -*- coding: utf-8 -*-
"""One-off patch: replace ai-knowledge-base section in settings.html."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / "templates" / "settings.html"

START = '            <section id="ai-knowledge-base">'
END = '            <section id="publishing">'

NEW_BLOCK = """            <section id="ai-knowledge-base" class="aikb-page">
                <div class="aikb-head">
                    <div>
                        <h2>Knowledge Base <span class="info" title="RAG: AI tra cứu dữ liệu nội bộ trước khi viết bài.">ⓘ</span></h2>
                        <p class="lead">Quản lý dữ liệu tham khảo để tạo bài viết chính xác với RAG</p>
                    </div>
                    <button type="button" class="apik-add-btn" id="aikbAdd"><span class="plus">+</span> Tạo KB</button>
                </div>

                <div id="aikbLoadErr" class="aip-load-err" hidden></div>

                <div id="aikbOnboarding" class="aikb-onboarding">
                    <div class="aikb-hero">
                        <div class="aikb-hero-top">
                            <div class="aikb-hero-ico" aria-hidden="true">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M6 4h12a2 2 0 0 1 2 2v14l-4-2-4 2-4-2-4 2V6a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M9 8h6M9 12h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
                            </div>
                            <div>
                                <h3 class="aikb-hero-title">Knowledge Base &amp; RAG</h3>
                                <p class="aikb-hero-desc">RAG (Retrieval-Augmented Generation) cho phép AI tra cứu dữ liệu nội bộ của bạn trước khi viết bài. Thay vì dựa vào kiến thức chung, AI sẽ tham khảo chính xác từ tài liệu bạn cung cấp — giúp nội dung đúng, đủ và nhất quán.</p>
                            </div>
                        </div>
                        <button type="button" class="aikb-hero-cta" id="aikbHeroCreate">
                            <span class="plus">+</span> Tạo Knowledge Base đầu tiên <span aria-hidden="true">→</span>
                        </button>
                    </div>

                    <h3 class="aikb-section-title">Quy trình hoạt động</h3>
                    <div class="aikb-workflow">
                        <article class="aikb-step">
                            <div class="aikb-step-ico" aria-hidden="true">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                            </div>
                            <h4>Tạo Knowledge Base</h4>
                            <p>Tạo KB cho dự án — nơi lưu trữ dữ liệu tham khảo riêng.</p>
                        </article>
                        <article class="aikb-step">
                            <div class="aikb-step-ico" aria-hidden="true">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 16V4m0 0 4 4m-4-4 4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                            </div>
                            <h4>Import tài liệu</h4>
                            <p>Dán văn bản, upload file (.txt, .md, .html) hoặc import hàng loạt từ CSV.</p>
                        </article>
                        <article class="aikb-step">
                            <div class="aikb-step-ico" aria-hidden="true">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M6.3 6.3l2.1 2.1M15.6 15.6l2.1 2.1M6.3 17.7l2.1-2.1M15.6 8.4l2.1-2.1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.6"/></svg>
                            </div>
                            <h4>Tự động xử lý</h4>
                            <p>Hệ thống cắt nhỏ (chunking) và tạo embedding vector cho từng đoạn.</p>
                        </article>
                        <article class="aikb-step">
                            <div class="aikb-step-ico" aria-hidden="true">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
                            </div>
                            <h4>AI viết bài với RAG</h4>
                            <p>Khi viết bài, AI tra cứu KB để lấy thông tin chính xác, có nguồn dẫn.</p>
                        </article>
                    </div>

                    <div class="aikb-info-grid">
                        <div class="aikb-panel">
                            <h3>Lợi ích khi dùng RAG</h3>
                            <ul class="aikb-benefits">
                                <li><span class="aikb-check" aria-hidden="true">✓</span> Bài viết chính xác hơn nhờ dữ liệu thực tế từ doanh nghiệp.</li>
                                <li><span class="aikb-check" aria-hidden="true">✓</span> Giảm ảo giác AI (hallucination) — AI chỉ nói những gì có trong KB.</li>
                                <li><span class="aikb-check" aria-hidden="true">✓</span> Thống nhất thông tin sản phẩm, giá cả, chính sách trên mọi bài viết.</li>
                                <li><span class="aikb-check" aria-hidden="true">✓</span> Hỗ trợ nhiều định dạng: văn bản, Markdown, HTML, CSV.</li>
                            </ul>
                        </div>
                        <div class="aikb-panel">
                            <h3><span aria-hidden="true">💡</span> Gợi ý nội dung nên import</h3>
                            <div class="aikb-tags">
                                <span class="aikb-tag">Thông tin sản phẩm / dịch vụ</span>
                                <span class="aikb-tag">Báo cáo, nghiên cứu ngành</span>
                                <span class="aikb-tag">FAQ, chính sách công ty</span>
                                <span class="aikb-tag">Bài viết tham khảo chất lượng</span>
                                <span class="aikb-tag">Dữ liệu kỹ thuật, thông số</span>
                                <span class="aikb-tag">Nội dung đào tạo nội bộ</span>
                            </div>
                            <p class="aikb-panel-foot">Nội dung càng chất lượng và có cấu trúc rõ ràng (tiêu đề, đoạn), AI càng tra cứu chính xác hơn.</p>
                        </div>
                    </div>
                </div>

                <div id="aikbListSection" class="aikb-list-section" hidden>
                    <h3 class="aikb-list-head">Knowledge bases của bạn</h3>
                    <div id="aikbGrid" class="aikb-grid" aria-live="polite"></div>
                </div>
            </section>
"""


def _fix_tags(s: str) -> str:
    return (
        s.replace("</div>", "</div>")
        .replace("<div>", "<div>")
        .replace("<div ", "<div ")
    )


def main():
    text = SETTINGS.read_text(encoding="utf-8")
    i0 = text.find(START)
    i1 = text.find(END)
    if i0 < 0 or i1 < 0 or i1 <= i0:
        raise SystemExit(f"markers not found: {i0}, {i1}")
    block = _fix_tags(NEW_BLOCK)
    SETTINGS.write_text(text[:i0] + block + text[i1:], encoding="utf-8")
    print("Patched", SETTINGS)


if __name__ == "__main__":
    main()
