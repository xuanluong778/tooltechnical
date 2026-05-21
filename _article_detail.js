    let _articleDetailProjectId = "";
    const articleDetailBackdropEl = byId("articleDetailBackdrop");
    const articleDetailModalEl = byId("articleDetailModal");
    const articleDetailBodyEl = byId("articleDetailBody");
    const closeArticleDetailModal = () => {
        if (articleDetailBackdropEl) articleDetailBackdropEl.classList.remove("open");
        if (articleDetailModalEl) {
            articleDetailModalEl.classList.remove("open");
            articleDetailModalEl.setAttribute("aria-hidden", "true");
        }
        _articleDetailProjectId = "";
    };
    const btnArticleDetailBackEl = byId("btnArticleDetailBack");
    const btnArticleDetailCloseEl = byId("btnArticleDetailClose");
    if (btnArticleDetailBackEl) btnArticleDetailBackEl.addEventListener("click", closeArticleDetailModal);
    if (btnArticleDetailCloseEl) {
        btnArticleDetailCloseEl.addEventListener("click", () => {
            closeArticleDetailModal();
            closeSiteArticlesModal();
        });
    }
    if (articleDetailBackdropEl) {
        articleDetailBackdropEl.addEventListener("click", (ev) => {
            if (ev.target === articleDetailBackdropEl) closeArticleDetailModal();
        });
    }
    const _adEscapeHtml = (s) =>
        String(s || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    const _parseIntroFromOutline = (outlineText) => {
        const intro = { hook: "", problem: "", promise: "" };
        const lines = String(outlineText || "").split(/\r?\n/);
        let inIntro = false;
        for (const raw of lines) {
            const line = String(raw || "").trim();
            if (/^##\s+/.test(line)) {
                if (inIntro) break;
                if (/giới\s*thiệu|introduction/i.test(line)) inIntro = true;
                continue;
            }
            if (/^#\s+/.test(line) && !/^##/.test(line)) continue;
            const labeled =
                line.match(/^(?:[-*]\s+)?(?:\*\*)?(Hook|Problem|Promise|Vấn đề|Lời hứa)(?:\*\*)?\s*[:：]\s*(.+)$/i) ||
                line.match(/^(?:[-*]\s+)?(Hook|Problem|Promise)\s*[-–]\s*(.+)$/i);
            if (labeled) {
                const key = labeled[1].toLowerCase();
                const val = labeled[2].trim();
                if (key === "hook") intro.hook = val;
                else if (key === "problem" || key === "vấn đề") intro.problem = val;
                else intro.promise = val;
                continue;
            }
            if (inIntro) {
                const li = line.match(/^[-*]\s+(.+)$/);
                if (!li) continue;
                const t = li[1];
                if (/^hook\s*[:：]/i.test(t)) intro.hook = t.replace(/^hook\s*[:：]\s*/i, "").trim();
                else if (/^problem|^vấn đề/i.test(t))
                    intro.problem = t.replace(/^(?:problem|vấn đề)\s*[:：]\s*/i, "").trim();
                else if (/^promise|^lời hứa/i.test(t))
                    intro.promise = t.replace(/^(?:promise|lời hứa)\s*[:：]\s*/i, "").trim();
            }
        }
        return intro;
    };
    const _splitMetaIntro = (meta) => {
        const t = String(meta || "").trim();
        if (!t) return { hook: "", problem: "", promise: "" };
        const parts = t.split(/(?<=[.!?…])\s+/).filter((x) => x.trim());
        return {
            hook: parts[0] || "",
            problem: parts[1] || "",
            promise: parts.slice(2).join(" ") || "",
        };
    };
    const _estimateSectionWords = (sec) => {
        const n = (sec.bullets || []).join(" ").split(/\s+/).filter(Boolean).length;
        const base = Math.max(180, n * 45 + String(sec.title || "").split(/\s+/).length * 12);
        return `~${Math.min(920, base)} words`;
    };
    const _parseOutlineSections = (outlineText) => {
        const lines = String(outlineText || "").split(/\r?\n/);
        const sections = [];
        let cur = null;
        for (const raw of lines) {
            const line = String(raw || "").trim();
            if (!line) continue;
            if (/^#\s+/.test(line) && !/^##/.test(line)) continue;
            const h2 = line.match(/^##\s+(.+)$/);
            if (h2) {
                const title = h2[1].trim();
                if (/giới\s*thiệu|introduction/i.test(title)) continue;
                if (cur) sections.push(cur);
                cur = { title, bullets: [] };
                continue;
            }
            const h3 = line.match(/^###\s+(.+)$/);
            if (h3 && cur) {
                cur.bullets.push(h3[1].trim());
                continue;
            }
            const li = line.match(/^[-*]\s+(.+)$/) || line.match(/^\d+[.)]\s+(.+)$/);
            if (li && cur) cur.bullets.push(li[1].trim());
        }
        if (cur) sections.push(cur);
        const conclusionIdx = sections.findIndex((s) => /kết\s*luận|tổng\s*kết|conclusion/i.test(s.title || ""));
        let conclusion = null;
        if (conclusionIdx >= 0) {
            const c = sections.splice(conclusionIdx, 1)[0];
            conclusion = {
                summary: (c.bullets || [])[0] || c.title || "",
                cta: (c.bullets || []).slice(1).join(" ") || "",
            };
        }
        return {
            sections: sections.map((s, i) => ({
                num: i + 1,
                title: s.title,
                bullets: s.bullets.length ? s.bullets : ["Nội dung triển khai theo mục này trong bài viết."],
                words: _estimateSectionWords(s),
            })),
            conclusion,
        };
    };
    const _seoCharClass = (len, min, max) => {
        if (len >= min && len <= max) return "ok";
        if (len > 0) return "warn";
        return "";
    };
    const _projectProgressSteps = (p) => {
        const pk = String(p.primary_keyword || "").trim();
        const outline = String(p.outline_content || "").trim();
        const content = String(p.content || "").trim();
        const thumb = String(p.featured_image || "").trim();
        const hasSection = /^#{2,3}\s/m.test(outline) || /<h[23]\b/i.test(content);
        return [
            { key: "research", label: "Research", done: !!pk },
            { key: "outline", label: "Outline", done: !!outline, active: !!outline && !content },
            { key: "content", label: "Content", done: !!content },
            { key: "thumb", label: "Thumb", done: !!thumb },
            { key: "section", label: "Section", done: hasSection },
        ];
    };
    const renderArticleDetail = (p) => {
        if (!articleDetailBodyEl || !p) return;
        const title = String(p.title || p.primary_keyword || "Bài viết").trim();
        const pk = String(p.primary_keyword || "").trim();
        const meta = String(p.meta_description || "").trim();
        const seoTitle = title;
        const st = articleStatusLabel(p.status || (p.content && p.outline_content ? "ready" : "draft"));
        const fromOutline = _parseIntroFromOutline(p.outline_content || "");
        const fromMeta = _splitMetaIntro(meta);
        const intro = {
            hook: fromOutline.hook || fromMeta.hook,
            problem: fromOutline.problem || fromMeta.problem,
            promise: fromOutline.promise || fromMeta.promise || meta,
        };
        const parsed = _parseOutlineSections(p.outline_content || "");
        const tags = [];
        if (pk) tags.push(pk);
        const secKw = p.secondary_keywords;
        if (Array.isArray(secKw)) secKw.forEach((k) => tags.push(String(k)));
        else if (typeof secKw === "string") {
            secKw.split(",").forEach((k) => {
                const t = k.trim();
                if (t) tags.push(t);
            });
        }
        (p.tags || []).forEach((k) => {
            const t = String(k).trim();
            if (t) tags.push(t);
        });
        const uniqTags = [];
        const seenTag = new Set();
        tags.forEach((t) => {
            const k = t.toLowerCase();
            if (!k || seenTag.has(k)) return;
            seenTag.add(k);
            uniqTags.push(t);
        });
        const steps = _projectProgressSteps(p);
        const titleLen = seoTitle.length;
        const metaLen = meta.length;
        let html = "";
        html += '<div class="ad-hero">';
        html += "<div>";
        html += '<div class="ad-hero-title-row">';
        html += `<div class="ad-hero-title">${_adEscapeHtml(title)}</div>`;
        html += `<span class="ad-badge ${st.cls}">${_adEscapeHtml(st.text)}</span>`;
        html += "</div>";
        html += `<div class="ad-kw-line">Keyword: <strong>${_adEscapeHtml(pk || "—")}</strong></div>`;
        html += "</div>";
        html += '<div class="ad-hero-actions">';
        html += '<button type="button" class="mini-btn" id="btnArticleDetailEdit">Chỉnh sửa</button>';
        html += '<button type="button" class="mini-btn primary" id="btnArticleDetailPublish">Publish</button>';
        html += "</div></div>";
        html += '<div class="ad-progress">';
        steps.forEach((s) => {
            const cls = s.done ? "done" : s.active ? "active" : "";
            const icon = s.done ? "✓" : s.active ? "●" : "○";
            html += `<div class="ad-step ${cls}"><span class="ad-step-icon">${icon}</span>${_adEscapeHtml(s.label)}</div>`;
        });
        const pending = st.cls === "ready" ? "Pending review" : st.text;
        html += `<div class="ad-step"><span class="ad-step-icon">⏳</span>${_adEscapeHtml(pending)}</div>`;
        html += "</div>";
        html += '<div class="ad-toolbar">';
        html += '<button type="button" class="mini-btn" id="btnArticleDetailEdit2">Edit</button>';
        html += '<button type="button" class="mini-btn" id="btnArticleDetailRegenOutline">Regenerate outline</button>';
        html += "</div>";
        html += '<div class="ad-panel"><h3>SEO</h3>';
        html += '<div class="ad-seo-row"><div class="ad-seo-label">SEO Title</div>';
        html += `<div class="ad-seo-val">${_adEscapeHtml(seoTitle)}</div>`;
        html += `<div class="ad-seo-count ${_seoCharClass(titleLen, 50, 60)}">${titleLen}/60 chars</div></div>`;
        html += '<div class="ad-seo-row"><div class="ad-seo-label">Meta Description</div>';
        html += `<div class="ad-seo-val">${_adEscapeHtml(meta || "—")}</div>`;
        html += `<div class="ad-seo-count ${_seoCharClass(metaLen, 120, 160)}">${metaLen}/160 chars</div></div></div>`;
        html += '<div class="ad-panel"><h3>Introduction</h3><div class="ad-intro-grid">';
        html += `<div class="ad-intro-block hook"><div class="lbl">Hook</div><p>${_adEscapeHtml(intro.hook || "—")}</p></div>`;
        html += `<div class="ad-intro-block problem"><div class="lbl">Problem</div><p>${_adEscapeHtml(intro.problem || "—")}</p></div>`;
        html += `<div class="ad-intro-block promise"><div class="lbl">Promise</div><p>${_adEscapeHtml(intro.promise || "—")}</p></div></div></div>`;
        html += `<div class="ad-panel"><h3>Sections (${parsed.sections.length})</h3>`;
        parsed.sections.forEach((sec) => {
            html += '<div class="ad-section-card"><div class="ad-section-head">';
            html += `<span class="ad-section-num">${sec.num}</span>`;
            html += `<div class="ad-section-title">${_adEscapeHtml(sec.title)}</div>`;
            html += `<span class="ad-section-wc">${_adEscapeHtml(sec.words)}</span></div>`;
            html += '<ul class="ad-section-body">';
            sec.bullets.forEach((b) => {
                html += `<li>${_adEscapeHtml(b)}</li>`;
            });
            html += "</ul></div>";
        });
        html += "</div>";
        const conc = parsed.conclusion;
        html += '<div class="ad-panel"><h3>Conclusion</h3><div class="ad-intro-grid">';
        html += `<div class="ad-intro-block promise"><div class="lbl">Summary</div><p>${_adEscapeHtml(conc && conc.summary ? conc.summary : "Tóm tắt nội dung chính của bài viết.")}</p></div>`;
        html += `<div class="ad-intro-block hook"><div class="lbl">Call to Action</div><p>${_adEscapeHtml(conc && conc.cta ? conc.cta : "Kêu gọi hành động phù hợp với mục tiêu bài viết.")}</p></div></div></div>`;
        html += '<div class="ad-panel"><h3>SEO Keywords</h3><div class="ad-kw-tags">';
        uniqTags.slice(0, 24).forEach((t) => {
            html += `<span class="ad-kw-tag">${_adEscapeHtml(t)}</span>`;
        });
        html += "</div></div>";
        articleDetailBodyEl.innerHTML = html.replace(/<\/?motion\.div>/gi, (m) => (m.startsWith("</") ? "</div>" : "<div>")).replace(/<motion\.div>/g, "<div>");
        const headTitle = byId("articleDetailHeadTitle");
        if (headTitle) headTitle.textContent = title.slice(0, 80);
        const wireEdit = async () => {
            closeArticleDetailModal();
            await loadProject(_articleDetailProjectId);
        };
        const btnEdit = byId("btnArticleDetailEdit");
        const btnEdit2 = byId("btnArticleDetailEdit2");
        if (btnEdit) btnEdit.addEventListener("click", wireEdit);
        if (btnEdit2) btnEdit2.addEventListener("click", wireEdit);
        const btnPub = byId("btnArticleDetailPublish");
        if (btnPub) {
            btnPub.addEventListener("click", async () => {
                closeArticleDetailModal();
                await loadProject(_articleDetailProjectId);
                const pub = byId("btnPublishNow");
                if (pub) pub.click();
            });
        }
        const btnRegen = byId("btnArticleDetailRegenOutline");
        if (btnRegen) {
            btnRegen.addEventListener("click", async () => {
                closeArticleDetailModal();
                await loadProject(_articleDetailProjectId);
                const r = byId("btnOutlineRefresh");
                if (r) r.click();
            });
        }
    };
    const openArticleDetailModal = async (projectId) => {
        const pid = String(projectId || "").trim();
        if (!pid) return;
        _articleDetailProjectId = pid;
        if (articleDetailBodyEl) {
            articleDetailBodyEl.innerHTML = '<div class="hint">Đang tải chi tiết bài viết…</div>';
        }
        if (articleDetailBackdropEl) articleDetailBackdropEl.classList.add("open");
        if (articleDetailModalEl) {
            articleDetailModalEl.classList.add("open");
            articleDetailModalEl.setAttribute("aria-hidden", "false");
        }
        try {
            const res = await fetch(`/content-ai/projects/${encodeURIComponent(pid)}?ts=${Date.now()}`);
            const data = await res.json().catch(() => ({}));
            if (!res.ok) throw new Error((data && data.detail) ? data.detail : "Không tải được bài viết.");
            renderArticleDetail(data);
        } catch (e) {
            if (articleDetailBodyEl) {
                articleDetailBodyEl.innerHTML = `<div class="hint">${_adEscapeHtml(String(e.message || e))}</div>`;
            }
        }
    };
