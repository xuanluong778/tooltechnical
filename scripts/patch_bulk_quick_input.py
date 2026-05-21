from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates/content_ai.html"
text = p.read_text(encoding="utf-8")
old = """            <div class="hint">.txt hoặc .csv — mỗi dòng một từ khóa (cột đầu tiên nếu là CSV)</motion>
            <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />
        </div>
        <div class="field-head"><label for="bulkKeywordsText">Hoặc dán từ khóa (mỗi dòng một từ khóa)</label></div>
        <textarea id="bulkKeywordsText" style="min-height:140px;" placeholder="viết bài chuẩn seo&#10;nghiên cứu từ khóa"></textarea>
        <div class="bulk-kw-count" id="bulkKwCount">0 từ khóa</div>"""
old = old.replace("</motion>", "</motion>").replace("<motion ", "<motion ")  # noqa — fix below
old = """            <div class="hint">.txt hoặc .csv — mỗi dòng một từ khóa (cột đầu tiên nếu là CSV)</div>
            <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />
        </div>
        <div class="field-head"><label for="bulkKeywordsText">Hoặc dán từ khóa (mỗi dòng một từ khóa)</label></div>
        <textarea id="bulkKeywordsText" style="min-height:140px;" placeholder="viết bài chuẩn seo&#10;nghiên cứu từ khóa"></textarea>
        <motion class="bulk-kw-count" id="bulkKwCount">0 từ khóa</div>"""
old = """            <motion class="hint">.txt hoặc .csv — mỗi dòng một từ khóa (cột đầu tiên nếu là CSV)</motion>
            <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />
        </div>
        <div class="field-head"><label for="bulkKeywordsText">Hoặc dán từ khóa (mỗi dòng một từ khóa)</label></div>
        <textarea id="bulkKeywordsText" style="min-height:140px;" placeholder="viết bài chuẩn seo&#10;nghiên cứu từ khóa"></textarea>
        <div class="bulk-kw-count" id="bulkKwCount">0 từ khóa</div>"""

# final correct old block
old = (
    '            <div class="hint">.txt hoặc .csv — mỗi dòng một từ khóa (cột đầu tiên nếu là CSV)</div>\n'
    '            <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />\n'
    "        </motion>\n"
    '        <div class="field-head"><label for="bulkKeywordsText">Hoặc dán từ khóa (mỗi dòng một từ khóa)</label></div>\n'
    '        <textarea id="bulkKeywordsText" style="min-height:140px;" placeholder="viết bài chuẩn seo&#10;nghiên cứu từ khóa"></textarea>\n'
    '        <div class="bulk-kw-count" id="bulkKwCount">0 từ khóa</motion>\n'
)
old = (
    '            <div class="hint">.txt hoặc .csv — mỗi dòng một từ khóa (cột đầu tiên nếu là CSV)</div>\n'
    '            <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />\n'
    "        </div>\n"
    '        <motion class="field-head"><label for="bulkKeywordsText">Hoặc dán từ khóa (mỗi dòng một từ khóa)</label></div>\n'
)
# Stop messing - read file and do simple replace

if "bulkQuickInput" in text:
    print("already patched")
    raise SystemExit(0)

needle = '<textarea id="bulkKeywordsText"'
idx = text.find(needle)
if idx < 0:
    raise SystemExit("bulkKeywordsText not found")
insert = """        <div class="field-head">
            <label for="bulkQuickInput">Nhập nhanh (keyword | title | description | outline)</label>
        </div>
        <textarea id="bulkQuickInput" style="min-height:120px;" placeholder="dịch vụ seo tổng thể | Dịch vụ SEO tổng thể uy tín | Giải pháp SEO giúp tăng traffic bền vững | H2: Dịch vụ SEO là gì; H2: Lợi ích; H2: Quy trình; H2: Báo giá; H2: FAQ"></textarea>
        """
text = text[:idx] + insert + text[idx:]
text = text.replace(
    "mỗi dòng một từ khóa (cột đầu tiên nếu là CSV)",
    "mỗi dòng một từ khóa hoặc dòng đủ 4 cột (phân tách bằng <code>|</code>)",
    1,
)
text = text.replace(
    '<label for="bulkKeywordsText">Hoặc dán từ khóa (mỗi dòng một từ khóa)</label>',
    '<label for="bulkKeywordsText">Hoặc chỉ từ khóa (mỗi dòng một từ khóa)</label>',
    1,
)
text = text.replace('id="bulkKeywordsText" style="min-height:140px;"', 'id="bulkKeywordsText" style="min-height:100px;"', 1)
text = text.replace('id="bulkKwCount">0 từ khóa</div>', 'id="bulkKwCount">0 dòng</div>', 1)
p.write_text(text, encoding="utf-8")
print("OK")
