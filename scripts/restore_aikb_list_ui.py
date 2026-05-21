# -*- coding: utf-8 -*-
from pathlib import Path

D = "d" + "iv"
p = Path(__file__).resolve().parents[1] / "templates" / "settings.html"
t = p.read_text(encoding="utf-8")

old = f"""                <{D} id="aikbListSection" class="aikb-list-section" hidden>
                    <h3 class="aikb-list-head">Knowledge bases của bạn</h3>
                    <{D} id="aikbGrid" class="aikb-grid" aria-live="polite"></{D}>
                </{D}>"""

new = f"""                <{D} id="aikbGrid" class="aikb-grid" aria-live="polite"></{D}>
                <{D} id="aikbEmpty" class="aikb-empty" hidden>
                    Chưa có knowledge base — bấm <strong>+ Tạo KB</strong> để tạo bộ kiến thức đầu tiên.
                </{D}>
                <p class="card-hint" style="margin-top: 16px;">
                    Dữ liệu lưu tại <code style="color:#86efac;">data/ai_knowledge_bases.json</code>. Tài liệu RAG lưu tại <code style="color:#86efac;">data/knowledge_docs/</code>.
                </p>"""

if old not in t:
    raise SystemExit("list html block not found")
t = t.replace(old, new, 1)

# Replace buildCard function
start = "    const buildCard = (item) => {"
end = "        return card;\n    };"
i0 = t.find(start)
i1 = t.find(end, i0)
if i0 < 0 or i1 < 0:
    raise SystemExit("buildCard not found")
i1 += len(end)

new_build = """
    const snippet = (item) => {
        const parts = [item.products_services, item.key_facts, item.custom_instructions].filter(Boolean);
        const s = parts.join(" ").trim();
        return s.length > 180 ? s.slice(0, 177) + "…" : s;
    };

    const buildCard = (item) => {
        const card = document.createElement("article");
        card.className = "aikb-card" + (item.is_default ? " is-default" : "") + (item.enabled ? "" : " is-disabled");
        const brand = item.brand_name || item.name || "";
        const site = item.website_url || "";
        card.innerHTML =
            '<div class="aikb-card-top">' +
            '<h3 class="aikb-card-title">' + escapeHtml(item.name) + "</h3>" +
            (item.is_default ? '<span class="aikb-badge">Mặc định</span>' : "") +
            "</motion>" +
            '<p class="aikb-meta"><strong>Brand:</strong> ' + escapeHtml(brand || "—") +
            (site ? ' · <a href="' + escapeHtml(site) + '" target="_blank" rel="noopener" style="color:#86efac;">' + escapeHtml(site) + "</a>" : "") +
            "</p>" +
            '<p class="aikb-meta"><strong>Giọng văn:</strong> ' + escapeHtml(item.tone_label || item.tone || "") + "</p>" +
            '<p class="aikb-snippet">' + escapeHtml(snippet(item) || "Chưa có mô tả chi tiết.") + "</p>" +
            '<div class="aikb-card-actions">' +
            '<button type="button" class="btn-edit">Sửa</button>' +
            '<button type="button" class="btn-del">Xóa</button>' +
            "</motion>";

        card.querySelector(".btn-edit").addEventListener("click", () => openModal(item));
        card.querySelector(".btn-del").addEventListener("click", async () => {
            if (!confirm('Xóa knowledge base "' + (item.name || "") + '"?')) return;
            try {
                const r = await fetch("/api/settings/ai-knowledge-bases/" + encodeURIComponent(item.id), { method: "DELETE" });
                if (!r.ok) throw new Error("Xóa thất bại");
                await refresh();
            } catch (e) {
                alert(String(e.message || e));
            }
        });
        return card;
    };""".replace("</motion>", f"</{D}>").replace("<motion>", f"<{D}>")

t = t[:i0] + new_build + t[i1:]

# Fix JS init: listSectionEl -> emptyEl
t = t.replace(
    "    const listSectionEl = document.getElementById(\"aikbListSection\");",
    "    const emptyEl = document.getElementById(\"aikbEmpty\");",
)
t = t.replace(
    "            if (listSectionEl) listSectionEl.hidden = !hasItems;",
    "            if (emptyEl) emptyEl.hidden = hasItems;",
)

# Remove fmtNum if only used by old card - grep and remove block
import re
t = re.sub(r"\n    const fmtNum = \(n\) => \{[^}]+\};\n", "\n", t, count=1)

p.write_text(t, encoding="utf-8")
print("restored list ui")
