# -*- coding: utf-8 -*-
from pathlib import Path

D = "d" + "iv"
p = Path(__file__).resolve().parents[1] / "templates" / "settings.html"
t = p.read_text(encoding="utf-8")

old = f"""                <{D} id="aikbGrid" class="aikb-grid" aria-live="polite"></{D}>
                <{D} id="aikbEmpty" class="aikb-empty" hidden>
                    Chưa có knowledge base — bấm <strong>+ Tạo KB</strong> để tạo bộ kiến thức đầu tiên.
                </{D}>
                <p class="card-hint" style="margin-top: 16px;">
                    Dữ liệu lưu tại <code style="color:#86efac;">data/ai_knowledge_bases.json</code>. Tài liệu RAG lưu tại <code style="color:#86efac;">data/knowledge_docs/</code>.
                </p>"""

new = f"""                <{D} id="aikbListSection" class="aikb-list-section" hidden>
                    <{D} id="aikbGrid" class="aikb-grid" aria-live="polite"></{D}>
                </{D}>"""

if old not in t:
    raise SystemExit("html block not found")
t = t.replace(old, new, 1)

# Replace buildCard
start = "    const snippet = (item) => {"
end = "        return card;\n    };\n\n    const refresh = async () => {"
i0 = t.find(start)
i1 = t.find(end)
if i0 < 0 or i1 < 0:
    raise SystemExit("buildCard block not found")

new_js = """
    const fmtNum = (n) => {
        const x = Number(n) || 0;
        if (x >= 1000000) return (x / 1000000).toFixed(1) + "M";
        if (x >= 1000) return (x / 1000).toFixed(1) + "k";
        return String(x);
    };

    const buildCard = (item) => {
        const st = item.stats || {};
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
            '<div class="aikb-kb-card-head">' +
            '<motion class="aikb-kb-card-title-wrap">' +
            '<h3 class="aikb-kb-card-title">' + escapeHtml(item.name) + "</h3>" +
            (item.is_default ? '<span class="aikb-badge">Mặc định</span>' : "") +
            "</motion>" +
            '<div class="aikb-kb-card-actions">' +
            '<button type="button" class="aikb-btn-import btn-import"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 16V4m0 0 4 4m-4-4 4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg> Import</button>' +
            '<button type="button" class="aikb-btn-reindex btn-reindex"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 12a8 8 0 0 1 13.3-5.7M20 12a8 8 0 0 1-13.3 5.7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M17 6.3V2h4M7 17.7v4h-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg> Reindex</button>' +
            '<button type="button" class="aikb-btn-edit-kb btn-edit">Sửa</button>' +
            '<button type="button" class="aikb-btn-del-kb btn-del" title="Xóa KB" aria-label="Xóa KB"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m2 0v12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V7h12Z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button>' +
            "</motion>" +
            "</motion>" +
            '<div class="aikb-kb-metrics">' +
            '<div class="aikb-metric"><span class="aikb-metric-val">' + fmtNum(docs) + '</span><span class="aikb-metric-lbl">Tài liệu</span></motion>' +
            '<div class="aikb-metric"><span class="aikb-metric-val">' + fmtNum(chunks) + '</span><span class="aikb-metric-lbl">Chunks</span></motion>' +
            '<div class="aikb-metric"><span class="aikb-metric-val">' + embLabel + '</span><span class="aikb-metric-lbl">Embeddings</span></motion>' +
            '<motion class="aikb-metric"><span class="aikb-metric-val">' + fmtNum(tokens) + '</span><span class="aikb-metric-lbl">Tokens</span></motion>' +
            "</motion>" +
            (docs > 0 ? "" :
                '<div class="aikb-kb-empty">' +
                '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M8 4h8l2 4H6l2-4Z" stroke="currentColor" stroke-width="1.4"/><path d="M6 8v12h12V8" stroke="currentColor" stroke-width="1.4"/><path d="M10 12h4M10 16h4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>' +
                'Chưa có tài liệu nào. Nhấn <strong>Import</strong> để thêm.' +
                "</motion>");

        card.querySelector(".btn-import").addEventListener("click", () => openImportModal(item));
        card.querySelector(".btn-reindex").addEventListener("click", () => reindexKb(item));
        card.querySelector(".btn-edit").addEventListener("click", () => openModal(item));
        card.querySelector(".btn-del").addEventListener("click", async () => {
            if (!confirm('Xóa knowledge base "' + (item.name || "") + '" và toàn bộ tài liệu?')) return;
            try {
                const r = await fetch("/api/settings/ai-knowledge-bases/" + encodeURIComponent(item.id), { method: "DELETE" });
                if (!r.ok) throw new Error("Xóa thất bại");
                await refresh();
            } catch (e) {
                alert(String(e.message || e));
            }
        });
        return card;
    };

""".replace("</motion>", f"</{D}>").replace("<motion ", f"<{D} ").replace("<motion>", f"<{D}>")

t = t[:i0] + new_js + t[i1:]

t = t.replace(
    '    const emptyEl = document.getElementById("aikbEmpty");',
    '    const listSectionEl = document.getElementById("aikbListSection");',
)
t = t.replace(
    "            if (emptyEl) emptyEl.hidden = hasItems || (onboardingEl && !onboardingEl.hidden);",
    "            if (listSectionEl) listSectionEl.hidden = !hasItems;",
)

p.write_text(t, encoding="utf-8")
print("ok")
