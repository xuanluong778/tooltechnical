from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates/content_ai.html"
text = p.read_text(encoding="utf-8")

anchor = '        <motion class="bulk-kw-count" id="bulkKwCount">0 từ khóa</div>\n        <div class="bulk-kw-add-bar">'
anchor = '        <div class="bulk-kw-count" id="bulkKwCount">0 từ khóa</div>\n        <div class="bulk-kw-add-bar">'

insert = """        <div class="bulk-kw-count" id="bulkKwCount">0 từ khóa</div>
        <motion class="bulk-file-upload">
            <div><strong>Upload Excel hoặc file văn bản</strong></div>
            <div class="hint" style="margin-top:4px;">
                Hỗ trợ <code>.xlsx</code>, <code>.txt</code>, <code>.csv</code> — tự điền từ khóa, title, meta, outline, loại content, số từ, URL đối thủ (theo tên cột hoặc thứ tự cột).
            </div>
            <div class="bulk-file-row">
                <input type="file" id="bulkImportFile" accept=".xlsx,.txt,.csv,text/plain,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" />
                <button type="button" class="btn secondary" id="btnBulkImportFile">Tải file vào danh sách</button>
            </div>
            <div class="hint" id="bulkImportFileHint" style="margin-top:6px;"></motion>
        </div>
        <div class="bulk-kw-add-bar">"""

insert = insert.replace("<motion ", "<div ").replace("</motion>", "</div>")

if anchor not in text:
    raise SystemExit("anchor not found")
text = text.replace(anchor, insert, 1)

text = text.replace(
    "<summary>Import file / dán hàng loạt (tùy chọn)</summary>",
    "<summary>Dán text / import file phụ (tùy chọn)</summary>",
    1,
)
text = text.replace(
    '<motion class="hint">.txt / .csv — mỗi dòng một từ khóa hoặc <code>keyword | title | description | outline</code></div>',
    '<div class="hint">.txt / .csv / .xlsx — mỗi dòng hoặc theo cột Excel</div>',
    1,
)
old_accept = 'id="bulkKeywordsFile" accept=".txt,.csv,text/plain,text/csv"'
new_accept = 'id="bulkKeywordsFile" accept=".txt,.csv,.xlsx,text/plain,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"'
text = text.replace(old_accept, new_accept, 1)

p.write_text(text, encoding="utf-8")
print("OK")
