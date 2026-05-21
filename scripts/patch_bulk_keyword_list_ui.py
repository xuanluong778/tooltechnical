"""Patch content_ai.html: bulk keyword list UI + JS."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates/content_ai.html"
text = p.read_text(encoding="utf-8")

css_anchor = "        .bulk-job-item.pending { border-left: 3px solid #64748b; opacity: 0.85; }"
css_new = """        .bulk-job-item.pending { border-left: 3px solid #64748b; opacity: 0.85; }
        .bulk-kw-list { display: flex; flex-direction: column; gap: 10px; margin: 12px 0; max-height: 420px; overflow: auto; }
        .bulk-kw-card {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            background: rgba(15, 23, 42, 0.45);
            padding: 10px 12px;
        }
        .bulk-kw-row-main {
            display: grid;
            grid-template-columns: 1fr 100px 150px auto auto;
            gap: 8px;
            align-items: center;
        }
        .bulk-kw-row-main input, .bulk-kw-row-main select {
            height: 38px;
            font-size: 0.85rem;
        }
        .bulk-kw-keyword {
            font-weight: 600;
            color: #e2e8f0;
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .bulk-kw-details {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px dashed rgba(255, 255, 255, 0.12);
            display: none;
        }
        .bulk-kw-card.is-open .bulk-kw-details { display: block; }
        .bulk-kw-details-grid {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 8px;
            align-items: end;
        }
        .bulk-kw-details .field-mini { margin-bottom: 8px; }
        .bulk-kw-details .field-mini label {
            display: block;
            font-size: 0.72rem;
            color: #94a3b8;
            margin-bottom: 4px;
        }
        .bulk-kw-details input, .bulk-kw-details textarea {
            width: 100%;
            font-size: 0.85rem;
        }
        .bulk-kw-details textarea { min-height: 72px; resize: vertical; }
        .bulk-kw-add-bar {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 8px;
            margin-top: 8px;
        }
        .bulk-kw-add-bar input { height: 42px; }
        .bulk-kw-empty {
            padding: 20px;
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
            border: 1px dashed rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        .bulk-import-advanced { margin-top: 10px; }
        .bulk-import-advanced summary {
            cursor: pointer;
            color: #94a3b8;
            font-size: 0.82rem;
            user-select: none;
        }
        @media (max-width: 900px) {
            .bulk-kw-row-main { grid-template-columns: 1fr 1fr; }
        }"""

if ".bulk-kw-list" not in text:
    if css_anchor not in text:
        raise SystemExit("css anchor missing")
    text = text.replace(css_anchor, css_new, 1)

old_bulk_block = """        <motion class="bulk-drop">
            <div><strong>Upload danh sách từ khóa</strong></div>
            <div class="hint">.txt hoặc .csv — mỗi dòng một từ khóa hoặc dòng đủ 4 cột (phân tách bằng <code>|</code>)</div>
            <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />
        </div>
        <div class="field-head">
            <label for="bulkQuickInput">Nhập nhanh (keyword | title | description | outline)</label>
        </div>
        <textarea id="bulkQuickInput" style="min-height:120px;" placeholder="dịch vụ seo tổng thể | Dịch vụ SEO tổng thể uy tín | Giải pháp SEO giúp tăng traffic bền vững | H2: Dịch vụ SEO là gì; H2: Lợi ích; H2: Quy trình; H2: Báo giá; H2: FAQ"></textarea>
        <div class="field-head"><label for="bulkKeywordsText">Hoặc chỉ từ khóa (mỗi dòng một từ khóa)</label></div>
        <textarea id="bulkKeywordsText" style="min-height:100px;" placeholder="viết bài chuẩn seo&#10;nghiên cứu từ khóa"></textarea>
        <div class="bulk-kw-count" id="bulkKwCount">0 dòng</div>"""

old_bulk_block = """        <motion class="bulk-drop">
            <div><strong>Upload danh sách từ khóa</strong></div>
            <div class="hint">.txt hoặc .csv — mỗi dòng một từ khóa hoặc dòng đủ 4 cột (phân tách bằng <code>|</code>)</div>
            <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />
        </div>
        <div class="field-head">
            <label for="bulkQuickInput">Nhập nhanh (keyword | title | description | outline)</label>
        </div>
        <textarea id="bulkQuickInput" style="min-height:120px;" placeholder="dịch vụ seo tổng thể | Dịch vụ SEO tổng thể uy tín | Giải pháp SEO giúp tăng traffic bền vững | H2: Dịch vụ SEO là gì; H2: Lợi ích; H2: Quy trình; H2: Báo giá; H2: FAQ"></textarea>
        <div class="field-head"><label for="bulkKeywordsText">Hoặc chỉ từ khóa (mỗi dòng một từ khóa)</label></div>
        <textarea id="bulkKeywordsText" style="min-height:100px;" placeholder="viết bài chuẩn seo&#10;nghiên cứu từ khóa"></textarea>
        <div class="bulk-kw-count" id="bulkKwCount">0 dòng</div>"""

old_bulk_block = """        <div class="bulk-drop">
            <motion><strong>Upload danh sách từ khóa</strong></div>
            <div class="hint">.txt hoặc .csv — mỗi dòng một từ khóa hoặc dòng đủ 4 cột (phân tách bằng <code>|</code>)</div>
            <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />
        </div>
        <div class="field-head">
            <label for="bulkQuickInput">Nhập nhanh (keyword | title | description | outline)</label>
        </div>
        <textarea id="bulkQuickInput" style="min-height:120px;" placeholder="dịch vụ seo tổng thể | Dịch vụ SEO tổng thể uy tín | Giải pháp SEO giúp tăng traffic bền vững | H2: Dịch vụ SEO là gì; H2: Lợi ích; H2: Quy trình; H2: Báo giá; H2: FAQ"></textarea>
        <div class="field-head"><label for="bulkKeywordsText">Hoặc chỉ từ khóa (mỗi dòng một từ khóa)</label></div>
        <textarea id="bulkKeywordsText" style="min-height:100px;" placeholder="viết bài chuẩn seo&#10;nghiên cứu từ khóa"></textarea>
        <div class="bulk-kw-count" id="bulkKwCount">0 dòng</motion>"""

# correct block from file
old_bulk_block = """        <div class="bulk-drop">
            <motion><strong>Upload danh sách từ khóa</strong></motion>
            <div class="hint">.txt hoặc .csv — mỗi dòng một từ khóa hoặc dòng đủ 4 cột (phân tách bằng <code>|</code>)</div>
            <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />
        </div>
        <div class="field-head">
            <label for="bulkQuickInput">Nhập nhanh (keyword | title | description | outline)</label>
        </div>
        <textarea id="bulkQuickInput" style="min-height:120px;" placeholder="dịch vụ seo tổng thể | Dịch vụ SEO tổng thể uy tín | Giải pháp SEO giúp tăng traffic bền vững | H2: Dịch vụ SEO là gì; H2: Lợi ích; H2: Quy trình; H2: Báo giá; H2: FAQ"></textarea>
        <div class="field-head"><label for="bulkKeywordsText">Hoặc chỉ từ khóa (mỗi dòng một từ khóa)</label></div>
        <textarea id="bulkKeywordsText" style="min-height:100px;" placeholder="viết bài chuẩn seo&#10;nghiên cứu từ khóa"></textarea>
        <motion class="bulk-kw-count" id="bulkKwCount">0 dòng</div>"""

# Read exact from file
start = text.find('        <motion class="bulk-drop">')
if start < 0:
    start = text.find('        <div class="bulk-drop">')
end = text.find('        <div class="row">', start)
if start < 0 or end < 0:
    raise SystemExit(f"bulk block not found start={start} end={end}")
old_bulk_block = text[start:end]

new_bulk_block = """        <motion class="field-head"><label>Danh sách từ khóa</label></motion>
        <div id="bulkKeywordList" class="bulk-kw-list" aria-live="polite">
            <div class="bulk-kw-empty" id="bulkKeywordListEmpty">Chưa có từ khóa — nhập bên dưới và bấm <strong>Thêm</strong>.</div>
        </div>
        <div class="bulk-kw-count" id="bulkKwCount">0 từ khóa</div>
        <div class="bulk-kw-add-bar">
            <input type="text" id="bulkAddKeywordInput" placeholder="Nhập từ khóa rồi bấm Thêm…" autocomplete="off" />
            <button type="button" class="btn" id="btnBulkAddKeyword">Thêm</button>
        </div>
        <details class="bulk-import-advanced">
            <summary>Import file / dán hàng loạt (tùy chọn)</summary>
            <div class="bulk-drop" style="margin-top:10px;">
                <div class="hint">.txt / .csv — mỗi dòng một từ khóa hoặc <code>keyword | title | description | outline</code></div>
                <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />
            </div>
            <textarea id="bulkQuickInput" hidden aria-hidden="true"></textarea>
            <textarea id="bulkKeywordsText" style="min-height:80px;margin-top:8px;" placeholder="Dán nhiều dòng để import vào danh sách…"></textarea>
            <button type="button" class="btn secondary" id="btnBulkImportText" style="margin-top:8px;">Import vào danh sách</button>
        </details>
"""

new_bulk_block = new_bulk_block.replace("<motion ", "<div ").replace("</motion>", "</motion>").replace('</motion>', '</motion>')
new_bulk_block = new_bulk_block.replace("<motion class=\"field-head\">", '<motion class="field-head">')
# fix typos
new_bulk_block = """        <div class="field-head"><label>Danh sách từ khóa</label></div>
        <motion id="bulkKeywordList" class="bulk-kw-list" aria-live="polite">
            <div class="bulk-kw-empty" id="bulkKeywordListEmpty">Chưa có từ khóa — nhập bên dưới và bấm <strong>Thêm</strong>.</div>
        </div>
        <div class="bulk-kw-count" id="bulkKwCount">0 từ khóa</div>
        <div class="bulk-kw-add-bar">
            <input type="text" id="bulkAddKeywordInput" placeholder="Nhập từ khóa rồi bấm Thêm…" autocomplete="off" />
            <button type="button" class="btn" id="btnBulkAddKeyword">Thêm</button>
        </div>
        <details class="bulk-import-advanced">
            <summary>Import file / dán hàng loạt (tùy chọn)</summary>
            <div class="bulk-drop" style="margin-top:10px;">
                <div class="hint">.txt / .csv — mỗi dòng một từ khóa hoặc <code>keyword | title | description | outline</code></div>
                <input type="file" id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv" />
            </div>
            <textarea id="bulkQuickInput" hidden aria-hidden="true"></textarea>
            <textarea id="bulkKeywordsText" style="min-height:80px;margin-top:8px;" placeholder="Dán nhiều dòng để import vào danh sách…"></textarea>
            <button type="button" class="btn secondary" id="btnBulkImportText" style="margin-top:8px;">Import vào danh sách</button>
        </details>
"""
new_bulk_block = new_bulk_block.replace('id="bulkKeywordList" class="bulk-kw-list"', 'id="bulkKeywordList" class="bulk-kw-list"')
new_bulk_block = new_bulk_block.replace("<motion id=", "<div id=").replace("</motion>\n        </div>\n        <div class=\"bulk-kw-count\"", "</div>\n        <div class=\"bulk-kw-count\"")

text = text[:start] + new_bulk_block + text[end:]

# Update hint paragraph
text = text.replace(
    "Upload file .txt / .csv, nhập nhanh <code>keyword | title | description | outline</code>, hoặc dán mỗi dòng một từ khóa.",
    "Thêm từ khóa vào danh sách, mở <strong>Chi tiết</strong> để nhập volume, loại content, URL đối thủ và title/description/outline.",
    1,
)

p.write_text(text, encoding="utf-8")
print("HTML block OK", len(new_bulk_block))
