"""Replace aikb import modal HTML in settings.html."""
from pathlib import Path

NEW = r'''            <motion class="apik-modal-backdrop aikb-modal aikb-import-modal" id="aikbImportModal" role="dialog" aria-modal="true" aria-labelledby="aikbImportTitle" hidden>
                <div class="apik-modal">
                    <div class="apik-modal-head">
                        <h3 id="aikbImportTitle" class="aikb-import-head-title">
                            Import tài liệu
                            <span class="info" title="Thêm tài liệu vào Knowledge Base để AI tra cứu khi viết bài.">ⓘ</span>
                        </h3>
                        <button type="button" class="apik-modal-close" id="aikbImportClose" aria-label="Đóng">×</button>
                    </div>
                    <div class="aikb-form apik-form">
                        <p class="apik-help" id="aikbImportKbName" hidden></p>
                        <div class="aikb-import-tabs" id="aikbImportTabs" role="tablist">
                            <button type="button" class="aikb-import-tab is-active" data-pane="paste" role="tab" aria-selected="true">
                                <span class="tab-ico" aria-hidden="true">
                                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><rect x="8" y="8" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.6"/><rect x="4" y="4" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.6"/></svg>
                                </span>
                                Dán văn bản
                            </button>
                            <button type="button" class="aikb-import-tab" data-pane="file" role="tab" aria-selected="false">
                                <span class="tab-ico" aria-hidden="true">
                                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M12 16V4m0 0 4 4m-4-4 4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
                                </span>
                                Upload file
                            </button>
                            <button type="button" class="aikb-import-tab" data-pane="csv" role="tab" aria-selected="false">
                                <span class="tab-ico" aria-hidden="true">
                                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M8 4h8l2 4H6l2-4Z" stroke="currentColor" stroke-width="1.5"/><path d="M6 8v12h12V8" stroke="currentColor" stroke-width="1.5"/><path d="M9 11h6M9 15h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                                </span>
                                CSV
                            </button>
                        </div>

                        <div class="aikb-import-pane aikb-import-paste" id="aikbImportPanePaste" role="tabpanel">
                            <div class="aikb-import-label">
                                <span>Tiêu đề tài liệu</span>
                                <span class="info" title="Tên hiển thị khi tra cứu trong KB.">ⓘ</span>
                            </div>
                            <input type="text" id="aikbPasteTitle" placeholder="VD: Thông tin sản phẩm A, Báo cáo Q1 2024…">
                            <div class="aikb-import-label" style="margin-top:14px">
                                <span>Dán nội dung văn bản</span>
                                <span class="info" title="Nội dung sẽ được cắt chunk và embedding.">ⓘ</span>
                            </div>
                            <textarea id="aikbPasteText" placeholder="Dán nội dung văn bản tại đây…"></textarea>
                            <p class="aikb-import-paste-hint">Hỗ trợ: văn bản thường, Markdown, HTML</p>
                        </div>

                        <div class="aikb-import-pane" id="aikbImportPaneFile" role="tabpanel" hidden>
                            <div class="aikb-import-label">
                                <span>Chọn file</span>
                                <span class="info" title=".txt, .md, .html — tối đa 5MB.">ⓘ</span>
                            </motion>
                            <label class="aikb-file-zone" id="aikbFileZone">
                                <input type="file" id="aikbFileInput" accept=".txt,.md,.markdown,.html,.htm" hidden>
                                <span class="tab-ico" aria-hidden="true" style="display:block;margin:0 auto 10px">
                                    <svg width="36" height="36" viewBox="0 0 24 24" fill="none"><path d="M12 16V4m0 0 4 4m-4-4 4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
                                </span>
                                Kéo thả hoặc bấm để chọn file<br>
                                <span style="font-size:0.8rem;opacity:0.85">.txt, .md, .html</span>
                            </label>
                            <p class="apik-help" id="aikbFileName"></p>
                        </div>

                        <div class="aikb-import-pane" id="aikbImportPaneCsv" role="tabpanel" hidden>
                            <div class="aikb-import-label">
                                <span>Import CSV</span>
                                <span class="info" title="File CSV UTF-8.">ⓘ</span>
                            </div>
                            <label class="aikb-file-zone" id="aikbCsvZone">
                                <input type="file" id="aikbCsvInput" accept=".csv" hidden>
                                <span class="tab-ico" aria-hidden="true" style="display:block;margin:0 auto 10px">
                                    <svg width="36" height="36" viewBox="0 0 24 24" fill="none"><path d="M8 4h8l2 4H6l2-4Z" stroke="currentColor" stroke-width="1.5"/><path d="M6 8v12h12V8" stroke="currentColor" stroke-width="1.5"/></svg>
                                </span>
                                Chọn file .csv (tối đa 5MB)
                            </label>
                            <p class="apik-help" id="aikbCsvName"></p>
                        </div>

                        <div class="apik-modal-err" id="aikbImportErr"></div>
                        <motion class="aikb-import-foot">
                            <button type="button" class="btn-cancel" id="aikbImportCancel">Huỷ</button>
                            <button type="button" class="btn-submit" id="aikbImportSubmit">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M8 4h8l2 4H6l2-4Z" stroke="currentColor" stroke-width="1.5"/><path d="M6 8v12h12V8" stroke="currentColor" stroke-width="1.5"/><path d="M12 11v6M9 14h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                                Import
                            </button>
                        </div>
                    </div>
                </div>
            </div>
'''.replace("<motion ", "<motion ").replace("</motion>", "</div>")  # fix typos below

# fix motion typos in NEW
NEW = NEW.replace("<motion class=", "<div class=").replace("</motion>", "</motion>")

p = Path(__file__).resolve().parents[1] / "templates" / "settings.html"
text = p.read_text(encoding="utf-8")
start = text.find('            <div class="apik-modal-backdrop aikb-modal" id="aikbImportModal"')
end = text.find('            <div class="apik-modal-backdrop aikb-modal" id="aikbSearchModal"')
if start == -1 or end == -1:
    raise SystemExit(f"markers not found: {start} {end}")

# Build clean NEW without motion
NEW = '''            <div class="apik-modal-backdrop aikb-modal aikb-import-modal" id="aikbImportModal" role="dialog" aria-modal="true" aria-labelledby="aikbImportTitle" hidden>
                <motion class="apik-modal">
                    <div class="apik-modal-head">
                        <h3 id="aikbImportTitle" class="aikb-import-head-title">
                            Import tài liệu
                            <span class="info" title="Thêm tài liệu vào Knowledge Base để AI tra cứu khi viết bài.">ⓘ</span>
                        </h3>
                        <button type="button" class="apik-modal-close" id="aikbImportClose" aria-label="Đóng">×</button>
                    </div>
                    <div class="aikb-form apik-form">
                        <p class="apik-help" id="aikbImportKbName" hidden></p>
                        <div class="aikb-import-tabs" id="aikbImportTabs" role="tablist">
                            <button type="button" class="aikb-import-tab is-active" data-pane="paste" role="tab" aria-selected="true">
                                <span class="tab-ico" aria-hidden="true">
                                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><rect x="8" y="8" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.6"/><rect x="4" y="4" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.6"/></svg>
                                </span>
                                Dán văn bản
                            </button>
                            <button type="button" class="aikb-import-tab" data-pane="file" role="tab" aria-selected="false">
                                <span class="tab-ico" aria-hidden="true">
                                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M12 16V4m0 0 4 4m-4-4 4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
                                </span>
                                Upload file
                            </button>
                            <button type="button" class="aikb-import-tab" data-pane="csv" role="tab" aria-selected="false">
                                <span class="tab-ico" aria-hidden="true">
                                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M8 4h8l2 4H6l2-4Z" stroke="currentColor" stroke-width="1.5"/><path d="M6 8v12h12V8" stroke="currentColor" stroke-width="1.5"/><path d="M9 11h6M9 15h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                                </span>
                                CSV
                            </button>
                        </div>

                        <div class="aikb-import-pane aikb-import-paste" id="aikbImportPanePaste" role="tabpanel">
                            <div class="aikb-import-label">
                                <span>Tiêu đề tài liệu</span>
                                <span class="info" title="Tên hiển thị khi tra cứu trong KB.">ⓘ</span>
                            </div>
                            <input type="text" id="aikbPasteTitle" placeholder="VD: Thông tin sản phẩm A, Báo cáo Q1 2024…">
                            <div class="aikb-import-label" style="margin-top:14px">
                                <span>Dán nội dung văn bản</span>
                                <span class="info" title="Nội dung sẽ được cắt chunk và embedding.">ⓘ</span>
                            </div>
                            <textarea id="aikbPasteText" placeholder="Dán nội dung văn bản tại đây…"></textarea>
                            <p class="aikb-import-paste-hint">Hỗ trợ: văn bản thường, Markdown, HTML</p>
                        </div>

                        <div class="aikb-import-pane" id="aikbImportPaneFile" role="tabpanel" hidden>
                            <div class="aikb-import-label">
                                <span>Chọn file</span>
                                <span class="info" title=".txt, .md, .html — tối đa 5MB.">ⓘ</span>
                            </div>
                            <label class="aikb-file-zone" id="aikbFileZone">
                                <input type="file" id="aikbFileInput" accept=".txt,.md,.markdown,.html,.htm" hidden>
                                <span class="tab-ico" aria-hidden="true" style="display:block;margin:0 auto 10px">
                                    <svg width="36" height="36" viewBox="0 0 24 24" fill="none"><path d="M12 16V4m0 0 4 4m-4-4 4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
                                </span>
                                Kéo thả hoặc bấm để chọn file<br>
                                <span style="font-size:0.8rem;opacity:0.85">.txt, .md, .html</span>
                            </label>
                            <p class="apik-help" id="aikbFileName"></p>
                        </div>

                        <div class="aikb-import-pane" id="aikbImportPaneCsv" role="tabpanel" hidden>
                            <div class="aikb-import-label">
                                <span>Import CSV</span>
                                <span class="info" title="File CSV UTF-8.">ⓘ</span>
                            </div>
                            <label class="aikb-file-zone" id="aikbCsvZone">
                                <input type="file" id="aikbCsvInput" accept=".csv" hidden>
                                <span class="tab-ico" aria-hidden="true" style="display:block;margin:0 auto 10px">
                                    <svg width="36" height="36" viewBox="0 0 24 24" fill="none"><path d="M8 4h8l2 4H6l2-4Z" stroke="currentColor" stroke-width="1.5"/><path d="M6 8v12h12V8" stroke="currentColor" stroke-width="1.5"/></svg>
                                </span>
                                Chọn file .csv (tối đa 5MB)
                            </label>
                            <p class="apik-help" id="aikbCsvName"></p>
                        </div>

                        <div class="apik-modal-err" id="aikbImportErr"></motion>
                        <div class="aikb-import-foot">
                            <button type="button" class="btn-cancel" id="aikbImportCancel">Huỷ</button>
                            <button type="button" class="btn-submit" id="aikbImportSubmit">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M8 4h8l2 4H6l2-4Z" stroke="currentColor" stroke-width="1.5"/><path d="M6 8v12h12V8" stroke="currentColor" stroke-width="1.5"/><path d="M12 11v6M9 14h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                                Import
                            </button>
                        </div>
                    </div>
                </div>
            </div>

'''.replace("<motion class=", "<div class=").replace("</motion>", "</div>")

p.write_text(text[:start] + NEW + text[end:], encoding="utf-8")
print("OK")
