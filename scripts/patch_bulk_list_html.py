from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates/content_ai.html"
text = p.read_text(encoding="utf-8")
start = text.find('        <motion class="bulk-drop">')
if start < 0:
    start = text.find('        <div class="bulk-drop">')
end = text.find('        <div class="row">', start)
if start < 0 or end < 0:
    raise SystemExit(f"not found start={start} end={end}")

new = """        <motion class="field-head"><label>Danh sách từ khóa</label></div>
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
new = new.replace('<motion class="field-head">', '<div class="field-head">', 1)
p.write_text(text[:start] + new + text[end:], encoding="utf-8")
print("OK")
