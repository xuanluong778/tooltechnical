from pathlib import Path

p = Path("templates/content_ai.html")
text = p.read_text(encoding="utf-8")
marker = '<motion id="deleteConfirmBackdrop"'
marker = '<motion id="deleteConfirmBackdrop"'
marker = '<div id="deleteConfirmBackdrop" class="modal-backdrop"></div>'
if "bulkWriteModeModal" in text:
    print("already patched")
    raise SystemExit(0)
block = """<div id="bulkWriteModeBackdrop" class="modal-backdrop"></div>
<div id="bulkWriteModeModal" class="modal bulk-write-mode-modal" aria-hidden="true">
    <div class="modal-card">
        <div class="modal-head">
            <div class="modal-title">Chọn phạm vi viết bài</div>
        </div>
        <div class="modal-body">
            <p class="hint" style="margin:0 0 8px;">Chọn nhóm từ khóa sẽ đưa vào job viết hàng loạt.</p>
            <label class="bulk-write-mode-opt" for="bulkWriteModeAll">
                <input type="checkbox" id="bulkWriteModeAll" checked />
                <span>Viết tất cả<span class="sub">Gồm cả bài chưa setup đủ form — AI sẽ tự gợi ý title, meta, outline khi thiếu.</span></span>
            </label>
            <label class="bulk-write-mode-opt" for="bulkWriteModeSetup">
                <input type="checkbox" id="bulkWriteModeSetup" />
                <span>Viết bài đã Setup<span class="sub">Chỉ các dòng đã có số từ, title, mô tả (meta) và outline content.</span></span>
            </label>
            <p id="bulkWriteModeSummary"></p>
            <motion class="delete-confirm-actions">
                <button type="button" class="mini-btn" id="btnBulkWriteModeCancel">Hủy</button>
                <button type="button" class="mini-btn" id="btnBulkWriteModeOk" style="background:rgba(34,197,94,0.2);border-color:rgba(34,197,94,0.5);color:#86efac;">Bắt đầu viết</button>
            </div>
        </div>
    </div>
</motion>
"""
block = block.replace("<motion ", "<div ").replace("</motion>", "</div>")
if marker not in text:
    raise SystemExit("marker not found")
text = text.replace(marker, block + "\n" + marker, 1)
p.write_text(text, encoding="utf-8")
print("ok")
