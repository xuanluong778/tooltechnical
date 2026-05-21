from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates/content_ai.html"
text = p.read_text(encoding="utf-8")
bad = """        <div class="field-head"><label for="bulkKeywordsText">Hoặc chỉ từ khóa (mỗi dòng một từ khóa)</label></div>
                <motion class="field-head">
            <label for="bulkQuickInput">Nhập nhanh (keyword | title | description | outline)</label>
        </div>
        <textarea id="bulkQuickInput" style="min-height:120px;" placeholder="dịch vụ seo tổng thể | Dịch vụ SEO tổng thể uy tín | Giải pháp SEO giúp tăng traffic bền vững | H2: Dịch vụ SEO là gì; H2: Lợi ích; H2: Quy trình; H2: Báo giá; H2: FAQ"></textarea>
        <textarea id="bulkKeywordsText" """
bad = """        <div class="field-head"><label for="bulkKeywordsText">Hoặc chỉ từ khóa (mỗi dòng một từ khóa)</label></div>
                <div class="field-head">
            <label for="bulkQuickInput">Nhập nhanh (keyword | title | description | outline)</label>
        </div>
        <textarea id="bulkQuickInput" style="min-height:120px;" placeholder="dịch vụ seo tổng thể | Dịch vụ SEO tổng thể uy tín | Giải pháp SEO giúp tăng traffic bền vững | H2: Dịch vụ SEO là gì; H2: Lợi ích; H2: Quy trình; H2: Báo giá; H2: FAQ"></textarea>
        <textarea id="bulkKeywordsText" """
good = """        <div class="field-head">
            <label for="bulkQuickInput">Nhập nhanh (keyword | title | description | outline)</label>
        </div>
        <textarea id="bulkQuickInput" style="min-height:120px;" placeholder="dịch vụ seo tổng thể | Dịch vụ SEO tổng thể uy tín | Giải pháp SEO giúp tăng traffic bền vững | H2: Dịch vụ SEO là gì; H2: Lợi ích; H2: Quy trình; H2: Báo giá; H2: FAQ"></textarea>
        <div class="field-head"><label for="bulkKeywordsText">Hoặc chỉ từ khóa (mỗi dòng một từ khóa)</label></div>
        <textarea id="bulkKeywordsText" """
if bad not in text:
    raise SystemExit("block not found")
text = text.replace(bad, good, 1)
p.write_text(text, encoding="utf-8")
print("OK")
