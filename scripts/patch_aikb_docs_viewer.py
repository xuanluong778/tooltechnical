# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "templates" / "settings.html"
t = p.read_text(encoding="utf-8")

old_metric = (
    "            '<div class=\"aikb-metric\"><span class=\"aikb-metric-val\">' + fmtNum(docs) + "
    "'</span><span class=\"aikb-metric-lbl\">Tài liệu</span></div>' +"
)

new_metric = (
    "            '<div class=\"aikb-metric aikb-metric-docs' + (docs > 0 ? ' is-clickable' : '') + "
    "'\" data-action=\"docs\" tabindex=\"' + (docs > 0 ? '0' : '-1') + '\" title=\"' + "
    "(docs > 0 ? 'Xem danh sách tài liệu / sơ đồ tri thức' : '') + '\">"
    "<span class=\"aikb-metric-val\">' + fmtNum(docs) + '</span>"
    "<span class=\"aikb-metric-lbl\">Tài liệu</span></div>' +"
)

if old_metric not in t:
    raise SystemExit("old_metric not found")

t = t.replace(old_metric, new_metric, 1)

hook = """        const metricDocs = card.querySelector(".aikb-metric-docs");
        if (metricDocs && docs > 0) {
            const openDocs = () => openDocsModal(item);
            metricDocs.addEventListener("click", (ev) => { ev.stopPropagation(); openDocs(); });
            metricDocs.addEventListener("keydown", (ev) => {
                if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); openDocs(); }
            });
        }

"""

anchor = '        card.querySelector(".btn-import").addEventListener("click", () => openImportModal(item));'
if "openDocsModal" not in t:
    if anchor not in t:
        raise SystemExit("btn-import anchor not found")
    t = t.replace(anchor, hook + anchor, 1)

js_block = """
    let docsKbId = null;
    const docsModal = document.getElementById("aikbDocsModal");
    const docsListEl = document.getElementById("aikbDocsList");
    const docsErr = document.getElementById("aikbDocsErr");
    const docsKbName = document.getElementById("aikbDocsKbName");
    const docViewModal = document.getElementById("aikbDocViewModal");
    const docViewTitle = document.getElementById("aikbDocViewTitle");
    const docViewMeta = document.getElementById("aikbDocViewMeta");
    const docViewBody = document.getElementById("aikbDocViewBody");
    const docViewErr = document.getElementById("aikbDocViewErr");

    const closeDocViewModal = () => {
        if (docViewModal) { docViewModal.hidden = true; docViewModal.classList.remove("is-open"); }
    };
    const closeDocsModal = () => {
        docsKbId = null;
        if (docsModal) { docsModal.hidden = true; docsModal.classList.remove("is-open"); }
        closeDocViewModal();
    };
    const renderDocView = (doc) => {
        if (!docViewBody) return;
        const sections = Array.isArray(doc.sections) ? doc.sections : [];
        const isKg = !!doc.is_knowledge_graph;
        if (docViewTitle) docViewTitle.textContent = isKg ? "Sơ đồ tri thức" : (doc.title || "Tài liệu");
        if (docViewMeta) {
            docViewMeta.textContent = (doc.title || doc.filename || "") +
                " · " + (doc.chunk_count || 0) + " chunks · " +
                Number(doc.char_count || 0).toLocaleString("vi-VN") + " ký tự";
        }
        if (sections.length > 1) {
            docViewBody.innerHTML = sections.map((s) =>
                '<section class="aikb-doc-section"><h4>' + escapeHtml(s.title || "") +
                '</h4><pre>' + escapeHtml(s.body || "") + "</pre></section>"
            ).join("");
        } else {
            const body = sections[0] && sections[0].body ? sections[0].body : (doc.content || "");
            docViewBody.innerHTML = "<pre>" + escapeHtml(body) + "</pre>";
        }
    };
    const openDocViewer = async (kbId, docId) => {
        if (!docViewModal || !kbId || !docId) return;
        if (docViewErr) docViewErr.textContent = "";
        if (docViewBody) docViewBody.innerHTML = '<p class="apik-help">Đang tải tài liệu…</p>';
        docViewModal.hidden = false;
        docViewModal.classList.add("is-open");
        try {
            const r = await fetch(
                "/api/settings/ai-knowledge-bases/" + encodeURIComponent(kbId) +
                "/documents/" + encodeURIComponent(docId)
            );
            const data = await r.json().catch(() => ({}));
            if (!r.ok) throw new Error(typeof data.detail === "string" ? data.detail : ("HTTP " + r.status));
            renderDocView(data.document || {});
        } catch (e) {
            if (docViewBody) docViewBody.innerHTML = "";
            if (docViewErr) docViewErr.textContent = String(e.message || e);
        }
    };
    const openDocsModal = async (item) => {
        if (!docsModal || !item || !item.id) return;
        docsKbId = item.id;
        if (docsKbName) docsKbName.textContent = "Knowledge Base: " + (item.name || "");
        if (docsErr) docsErr.textContent = "";
        if (docsListEl) docsListEl.innerHTML = '<p class="apik-help">Đang tải…</p>';
        docsModal.hidden = false;
        docsModal.classList.add("is-open");
        try {
            const r = await fetch(
                "/api/settings/ai-knowledge-bases/" + encodeURIComponent(item.id) + "/documents"
            );
            const data = await r.json().catch(() => ({}));
            if (!r.ok) throw new Error(typeof data.detail === "string" ? data.detail : ("HTTP " + r.status));
            const docs = data.documents || [];
            if (!docsListEl) return;
            if (!docs.length) {
                docsListEl.innerHTML = '<p class="apik-help">Chưa có tài liệu. Bấm Import trên thẻ KB.</p>';
                return;
            }
            docsListEl.innerHTML = "";
            docs.forEach((d) => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "aikb-doc-row";
                const title = d.title || d.filename || "Tài liệu";
                btn.innerHTML =
                    "<span><strong>" + escapeHtml(title) + '</strong><span class="meta">' +
                    escapeHtml(String(d.chunk_count || 0)) + " chunks · " +
                    escapeHtml(String(d.token_estimate || 0)) + ' tokens</span></span><span aria-hidden="true">→</span>';
                btn.addEventListener("click", () => openDocViewer(item.id, d.id));
                docsListEl.appendChild(btn);
            });
        } catch (e) {
            if (docsListEl) docsListEl.innerHTML = "";
            if (docsErr) docsErr.textContent = String(e.message || e);
        }
    };
    ["aikbDocsClose", "aikbDocsCancel"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("click", closeDocsModal);
    });
    ["aikbDocViewClose", "aikbDocViewCancel"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("click", closeDocsModal);
    });
    const docViewBack = document.getElementById("aikbDocViewBack");
    if (docViewBack) docViewBack.addEventListener("click", () => { closeDocViewModal(); });
    if (docsModal) docsModal.addEventListener("click", (ev) => { if (ev.target === docsModal) closeDocsModal(); });
    if (docViewModal) docViewModal.addEventListener("click", (ev) => { if (ev.target === docViewModal) closeDocViewModal(); });

"""

js_anchor = '    const importModal = document.getElementById("aikbImportModal");'
if "let docsKbId" not in t:
    if js_anchor not in t:
        raise SystemExit("js_anchor not found")
    t = t.replace(js_anchor, js_block + js_anchor, 1)

p.write_text(t, encoding="utf-8")
print("patched settings.html")
