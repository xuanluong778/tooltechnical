# -*- coding: utf-8 -*-
from pathlib import Path

D = "motion"  # will be replaced below
D = "d" + "iv"

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / "templates" / "settings.html"


def tag(name=None, cls=None, close=False):
    if close:
        return f"</{D}>"
    attrs = f' class="{cls}"' if cls else ""
    return f"<{D}{attrs}>"


def main():
    text = SETTINGS.read_text(encoding="utf-8")

    head_old = (
        '                    <button type="button" class="apik-add-btn" id="aikbAdd"><span class="plus">+</span> Tạo KB</button>\n'
        "                </div>\n\n"
        '                <motion id="aikbLoadErr"'.replace("motion", D)
    )
    head_old = (
        '                    <button type="button" class="apik-add-btn" id="aikbAdd"><span class="plus">+</span> Tạo KB</button>\n'
        "                </div>\n\n"
        f'                <{D} id="aikbLoadErr"'
    )

    head_new = f"""                    {tag(cls="aikb-head-actions")}
                        <button type="button" class="aikb-btn-ghost" id="aikbTestSearch" title="Thử tra cứu RAG">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.8"/><path d="M20 20l-3-3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
                            Test Search
                        </button>
                        <button type="button" class="apik-add-btn" id="aikbAdd"><span class="plus">+</span> Tạo KB</button>
                    {tag(close=True)}
                {tag(close=True)}

                <{D} id="aikbLoadErr" class="aip-load-err" hidden></{D}>"""

    if head_old not in text:
        raise SystemExit("head_old not found")
    text = text.replace(head_old, head_new, 1)

    modal_marker = f"            {tag(close=True)}\n\n            <section id=\"search-console\">"
    if 'id="aikbImportModal"' not in text:
        modals = f"""
            <div class="apik-modal-backdrop aikb-modal" id="aikbImportModal" role="dialog" aria-modal="true" aria-labelledby="aikbImportTitle" hidden>
                <div class="apik-modal">
                    <div class="apik-modal-head">
                        <h3 id="aikbImportTitle">Import tài liệu</h3>
                        <button type="button" class="apik-modal-close" id="aikbImportClose" aria-label="Đóng">×</button>
                    </div>
                    <div class="aikb-form apik-form">
                        <p class="apik-help" id="aikbImportKbName" style="margin-top:0"></p>
                        <motion class="aikb-import-tabs" role="tablist">
                            <button type="button" class="aikb-import-tab is-active" data-pane="file">Upload file</button>
                            <button type="button" class="aikb-import-tab" data-pane="paste">Dán văn bản</button>
                        </div>
                        <div class="aikb-import-pane" id="aikbImportPaneFile">
                            <label class="aikb-file-zone" id="aikbFileZone">
                                <input type="file" id="aikbFileInput" accept=".txt,.md,.markdown,.html,.htm,.csv" hidden>
                                Chọn file .txt, .md, .html, .csv (tối đa 5MB)
                            </label>
                            <p class="apik-help" id="aikbFileName"></p>
                        </div>
                        <div class="aikb-import-pane" id="aikbImportPanePaste" hidden>
                            <label for="aikbPasteTitle">Tiêu đề (tuỳ chọn)</label>
                            <input type="text" id="aikbPasteTitle" placeholder="VD: FAQ sản phẩm">
                            <label for="aikbPasteText">Nội dung</label>
                            <textarea id="aikbPasteText" placeholder="Dán nội dung tài liệu…"></textarea>
                        </div>
                        <div class="apik-modal-err" id="aikbImportErr"></motion>
                        <div class="apik-modal-foot">
                            <button type="button" class="btn-cancel" id="aikbImportCancel">Cancel</button>
                            <button type="button" class="btn-submit" id="aikbImportSubmit">Import</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="apik-modal-backdrop aikb-modal" id="aikbSearchModal" role="dialog" aria-modal="true" aria-labelledby="aikbSearchTitle" hidden>
                <div class="apik-modal">
                    <div class="apik-modal-head">
                        <h3 id="aikbSearchTitle">Test Search</h3>
                        <button type="button" class="apik-modal-close" id="aikbSearchClose" aria-label="Đóng">×</button>
                    </div>
                    <div class="aikb-form apik-form">
                        <label for="aikbSearchKb">Knowledge Base</label>
                        <select id="aikbSearchKb"></select>
                        <label for="aikbSearchQuery">Truy vấn</label>
                        <input type="text" id="aikbSearchQuery" placeholder="Nhập từ khóa cần tra cứu…">
                        <div class="apik-modal-err" id="aikbSearchErr"></div>
                        <motion class="aikb-search-results" id="aikbSearchResults"></motion>
                        <div class="apik-modal-foot">
                            <button type="button" class="btn-cancel" id="aikbSearchCancel">Đóng</button>
                            <button type="button" class="btn-submit" id="aikbSearchRun">Tìm</button>
                        </div>
                    </div>
                </div>
            </div>

            <section id="search-console">"""
        modals = modals.replace("</motion>", f"</{D}>").replace("<motion ", f"<{D} ").replace("<motion>", f"<{D}>")
        if modal_marker not in text:
            raise SystemExit("modal marker not found")
        text = text.replace(modal_marker, modals, 1)

    js_start = "    const buildCard = (item) => {"
    js_end = "        return card;\n    };"
    i0 = text.find(js_start)
    i1 = text.find(js_end)
    if i0 < 0 or i1 < 0:
        raise SystemExit("JS card block not found")
    i1 += len(js_end)

    t = D
    js_new = f"""
    let kbItemsCache = [];
    let importKbId = null;

    const fmtNum = (n) => {{
        const x = Number(n) || 0;
        if (x >= 1000000) return (x / 1000000).toFixed(1) + "M";
        if (x >= 1000) return (x / 1000).toFixed(1) + "k";
        return String(x);
    }};

    const buildCard = (item) => {{
        const st = item.stats || {{}};
        const docs = st.documents || 0;
        const chunks = st.chunks || 0;
        const embDone = st.embeddings_done || 0;
        const embTotal = st.embeddings_total || 0;
        const tokens = st.tokens || 0;
        const embLabel = embTotal ? (embDone + "/" + embTotal) : "0/0";

        const card = document.createElement("article");
        card.className = "aikb-kb-card" + (item.is_default ? " is-default" : "") + (item.enabled ? "" : " is-disabled");
        card.dataset.kbId = item.id;

        card.innerHTML =
            '<{t} class="aikb-kb-card-head">' +
            '<{t} class="aikb-kb-card-title-wrap">' +
            '<h3 class="aikb-kb-card-title">' + escapeHtml(item.name) + "</h3>" +
            (item.is_default ? '<span class="aikb-badge">Mặc định</span>' : "") +
            "</{t}>" +
            '<{t} class="aikb-kb-card-actions">' +
            '<button type="button" class="aikb-btn-import btn-import"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 16V4m0 0 4 4m-4-4 4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg> Import</button>' +
            '<button type="button" class="aikb-btn-reindex btn-reindex"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 12a8 8 0 0 1 13.3-5.7M20 12a8 8 0 0 1-13.3 5.7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M17 6.3V2h4M7 17.7v4h-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg> Reindex</button>' +
            '<button type="button" class="aikb-btn-edit-kb btn-edit">Sửa</button>' +
            '<button type="button" class="aikb-btn-del-kb btn-del" title="Xóa KB" aria-label="Xóa KB"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m2 0v12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V7h12Z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button>' +
            "</{t}>" +
            "</{t}>" +
            '<{t} class="aikb-kb-metrics">' +
            '<{t} class="aikb-metric"><span class="aikb-metric-val">' + fmtNum(docs) + '</span><span class="aikb-metric-lbl">Tài liệu</span></{t}>' +
            '<{t} class="aikb-metric"><span class="aikb-metric-val">' + fmtNum(chunks) + '</span><span class="aikb-metric-lbl">Chunks</span></{t}>' +
            '<{t} class="aikb-metric"><span class="aikb-metric-val">' + embLabel + '</span><span class="aikb-metric-lbl">Embeddings</span></{t}>' +
            '<{t} class="aikb-metric"><span class="aikb-metric-val">' + fmtNum(tokens) + '</span><span class="aikb-metric-lbl">Tokens</span></{t}>' +
            "</{t}>" +
            (docs > 0 ? "" :
                '<{t} class="aikb-kb-empty">' +
                '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M8 4h8l2 4H6l2-4Z" stroke="currentColor" stroke-width="1.4"/><path d="M6 8v12h12V8" stroke="currentColor" stroke-width="1.4"/><path d="M10 12h4M10 16h4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>' +
                "Chưa có tài liệu nào. Nhấn <strong>Import</strong> để thêm." +
                "</{t}>");

        card.querySelector(".btn-import").addEventListener("click", () => openImportModal(item));
        card.querySelector(".btn-reindex").addEventListener("click", () => reindexKb(item));
        card.querySelector(".btn-edit").addEventListener("click", () => openModal(item));
        card.querySelector(".btn-del").addEventListener("click", async () => {{
            if (!confirm('Xóa knowledge base "' + (item.name || "") + '" và toàn bộ tài liệu?')) return;
            try {{
                const r = await fetch("/api/settings/ai-knowledge-bases/" + encodeURIComponent(item.id), {{ method: "DELETE" }});
                if (!r.ok) throw new Error("Xóa thất bại");
                await refresh();
            }} catch (e) {{
                alert(String(e.message || e));
            }}
        }});
        return card;
    }};"""

    text = text[:i0] + js_new + text[i1:]

    helper_anchor = "    if ((window.location.hash || \"\").split(\"?\")[0] === \"#ai-knowledge-base\") refresh();"
    if "openImportModal" not in text and helper_anchor in text:
        helpers = """
    const importModal = document.getElementById("aikbImportModal");
    const importErr = document.getElementById("aikbImportErr");
    const importKbLabel = document.getElementById("aikbImportKbName");
    const fileInput = document.getElementById("aikbFileInput");
    const fileNameEl = document.getElementById("aikbFileName");
    const pasteTitle = document.getElementById("aikbPasteTitle");
    const pasteText = document.getElementById("aikbPasteText");
    const importSubmit = document.getElementById("aikbImportSubmit");
    const searchModal = document.getElementById("aikbSearchModal");
    const searchKb = document.getElementById("aikbSearchKb");
    const searchQuery = document.getElementById("aikbSearchQuery");
    const searchResults = document.getElementById("aikbSearchResults");
    const searchErr = document.getElementById("aikbSearchErr");
    let importPane = "file";

    const setImportPane = (pane) => {
        importPane = pane;
        document.querySelectorAll(".aikb-import-tab").forEach((btn) => {
            btn.classList.toggle("is-active", btn.dataset.pane === pane);
        });
        const f = document.getElementById("aikbImportPaneFile");
        const p = document.getElementById("aikbImportPanePaste");
        if (f) f.hidden = pane !== "file";
        if (p) p.hidden = pane !== "paste";
    };

    document.querySelectorAll(".aikb-import-tab").forEach((btn) => {
        btn.addEventListener("click", () => setImportPane(btn.dataset.pane || "file"));
    });

    const openImportModal = (item) => {
        importKbId = item.id;
        if (importKbLabel) importKbLabel.textContent = "Knowledge Base: " + (item.name || "");
        if (importErr) importErr.textContent = "";
        if (fileInput) fileInput.value = "";
        if (fileNameEl) fileNameEl.textContent = "";
        if (pasteTitle) pasteTitle.value = "";
        if (pasteText) pasteText.value = "";
        setImportPane("file");
        if (importModal) { importModal.hidden = false; importModal.classList.add("is-open"); }
    };

    const closeImportModal = () => {
        importKbId = null;
        if (importModal) { importModal.hidden = true; importModal.classList.remove("is-open"); }
    };

    if (fileInput) {
        fileInput.addEventListener("change", () => {
            const f = fileInput.files && fileInput.files[0];
            if (fileNameEl) fileNameEl.textContent = f ? ("Đã chọn: " + f.name) : "";
        });
    }
    const fileZone = document.getElementById("aikbFileZone");
    if (fileZone && fileInput) {
        fileZone.addEventListener("click", (ev) => {
            if (ev.target !== fileInput) fileInput.click();
        });
    }

    const runImport = async () => {
        if (!importKbId) return;
        if (importErr) importErr.textContent = "";
        importSubmit.disabled = true;
        try {
            let r;
            if (importPane === "paste") {
                const body = { title: (pasteTitle && pasteTitle.value.trim()) || "", text: (pasteText && pasteText.value) || "" };
                if (!body.text.trim()) throw new Error("Cần dán nội dung.");
                r = await fetch("/api/settings/ai-knowledge-bases/" + encodeURIComponent(importKbId) + "/import-text", {
                    method: "POST",
                    headers: { "content-type": "application/json" },
                    body: JSON.stringify(body),
                });
            } else {
                const f = fileInput && fileInput.files && fileInput.files[0];
                if (!f) throw new Error("Chọn file để import.");
                const fd = new FormData();
                fd.append("file", f);
                r = await fetch("/api/settings/ai-knowledge-bases/" + encodeURIComponent(importKbId) + "/import", {
                    method: "POST",
                    body: fd,
                });
            }
            if (!r.ok) {
                const e = await r.json().catch(() => ({}));
                throw new Error(typeof e.detail === "string" ? e.detail : ("HTTP " + r.status));
            }
            closeImportModal();
            await refresh();
        } catch (e) {
            if (importErr) importErr.textContent = String(e.message || e);
        } finally {
            importSubmit.disabled = false;
        }
    };

    const reindexKb = async (item) => {
        if (!confirm('Reindex toàn bộ tài liệu trong "' + (item.name || "") + '"?')) return;
        try {
            const r = await fetch("/api/settings/ai-knowledge-bases/" + encodeURIComponent(item.id) + "/reindex", { method: "POST" });
            if (!r.ok) throw new Error("Reindex thất bại");
            await refresh();
        } catch (e) {
            alert(String(e.message || e));
        }
    };

    ["aikbImportClose", "aikbImportCancel"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("click", closeImportModal);
    });
    if (importSubmit) importSubmit.addEventListener("click", runImport);
    if (importModal) importModal.addEventListener("click", (ev) => { if (ev.target === importModal) closeImportModal(); });

    const fillSearchKbs = () => {
        if (!searchKb) return;
        searchKb.innerHTML = "";
        kbItemsCache.forEach((it) => {
            const opt = document.createElement("option");
            opt.value = it.id;
            opt.textContent = it.name;
            searchKb.appendChild(opt);
        });
    };

    const openSearchModal = () => {
        fillSearchKbs();
        if (searchErr) searchErr.textContent = "";
        if (searchResults) searchResults.innerHTML = "";
        if (searchQuery) searchQuery.value = "";
        if (searchModal) { searchModal.hidden = false; searchModal.classList.add("is-open"); }
    };
    const closeSearchModal = () => {
        if (searchModal) { searchModal.hidden = true; searchModal.classList.remove("is-open"); }
    };

    const runSearch = async () => {
        const kbId = searchKb && searchKb.value;
        const q = searchQuery && searchQuery.value.trim();
        if (!kbId || !q) { if (searchErr) searchErr.textContent = "Chọn KB và nhập truy vấn."; return; }
        if (searchErr) searchErr.textContent = "";
        try {
            const r = await fetch("/api/settings/ai-knowledge-bases/" + encodeURIComponent(kbId) + "/search", {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({ query: q, limit: 8 }),
            });
            if (!r.ok) throw new Error("Tìm thất bại");
            const data = await r.json();
            const hits = data.hits || [];
            if (!searchResults) return;
            if (!hits.length) {
                searchResults.innerHTML = '<p class="apik-help">Không có kết quả.</p>';
                return;
            }
            searchResults.innerHTML = hits.map((h) =>
                '<article class="aikb-search-hit"><strong>' + escapeHtml(h.document_title || "") +
                " · chunk " + escapeHtml(String(h.chunk_index)) + "</strong><p>" + escapeHtml(h.snippet || "") + "</p></article>"
            ).join("");
        } catch (e) {
            if (searchErr) searchErr.textContent = String(e.message || e);
        }
    };

    const testSearchBtn = document.getElementById("aikbTestSearch");
    if (testSearchBtn) testSearchBtn.addEventListener("click", openSearchModal);
    ["aikbSearchClose", "aikbSearchCancel"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("click", closeSearchModal);
    });
    const searchRun = document.getElementById("aikbSearchRun");
    if (searchRun) searchRun.addEventListener("click", runSearch);
    if (searchModal) searchModal.addEventListener("click", (ev) => { if (ev.target === searchModal) closeSearchModal(); });

"""
        text = text.replace(helper_anchor, helpers + "\n" + helper_anchor, 1)

    refresh_patch = "            const items = data.items || [];\n            grid.innerHTML = \"\";"
    if "kbItemsCache = items" not in text and refresh_patch in text:
        text = text.replace(
            refresh_patch,
            "            const items = data.items || [];\n            kbItemsCache = items;\n            grid.innerHTML = \"\";",
            1,
        )

    SETTINGS.write_text(text, encoding="utf-8")
    print("OK")


if __name__ == "__main__":
    main()
