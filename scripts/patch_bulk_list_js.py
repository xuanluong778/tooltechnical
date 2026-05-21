from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates/content_ai.html"
text = p.read_text(encoding="utf-8")

marker_start = "    const bulkKeywordsText = byId(\"bulkKeywordsText\");"
marker_end = "    const appendBulkLog = (line) => {"

i0 = text.find(marker_start)
i1 = text.find(marker_end)
if i0 < 0 or i1 < 0 or i1 <= i0:
    raise SystemExit(f"markers not found {i0} {i1}")

new_block = r'''    const bulkKeywordsText = byId("bulkKeywordsText");
    const bulkQuickInput = byId("bulkQuickInput");
    const bulkKeywordsFile = byId("bulkKeywordsFile");
    const bulkKwCount = byId("bulkKwCount");
    const bulkKeywordList = byId("bulkKeywordList");
    const bulkKeywordListEmpty = byId("bulkKeywordListEmpty");
    const bulkAddKeywordInput = byId("bulkAddKeywordInput");
    const btnBulkAddKeyword = byId("btnBulkAddKeyword");
    const btnBulkImportText = byId("btnBulkImportText");
    const bulkJobLog = byId("bulkJobLog");
    const bulkJobProgress = byId("bulkJobProgress");
    const bulkJobProgressFill = byId("bulkJobProgressFill");
    const bulkJobStatus = byId("bulkJobStatus");
    const bulkJobPct = byId("bulkJobPct");
    const bulkJobItems = byId("bulkJobItems");
    const BULK_CONTENT_TYPES = [
        { value: "", label: "Loại content" },
        { value: "blog", label: "Blog / Informational" },
        { value: "landing", label: "Landing dịch vụ" },
        { value: "category", label: "Trang danh mục" },
        { value: "comparison", label: "So sánh / Review" },
        { value: "howto", label: "Hướng dẫn How-to" },
        { value: "local", label: "Local / Địa phương" },
    ];
    let bulkKeywordRows = [];
    const _bulkRowId = () => `bk_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
    const parseBulkInputLine = (line) => {
        let raw = String(line || "").trim();
        if (!raw) return null;
        if (raw.startsWith('"') && raw.endsWith('"') && raw.length > 1) raw = raw.slice(1, -1).trim();
        let keyword = "";
        let custom_title = "";
        let custom_description = "";
        let custom_outline = "";
        if (raw.includes("|")) {
            const parts = raw.split("|").map((x) => x.trim());
            keyword = parts[0] || "";
            custom_title = parts[1] || "";
            custom_description = parts[2] || "";
            custom_outline = parts.slice(3).join(" | ").trim();
        } else if (raw.includes(",") && !/\bH[1-3]\s*:/i.test(raw)) {
            keyword = raw.split(",")[0].trim();
        } else {
            keyword = raw;
        }
        keyword = keyword.replace(/\s+/g, " ").trim();
        if (!keyword) return null;
        return { keyword, custom_title, custom_description, custom_outline };
    };
    const parseBulkItemsText = (raw) => {
        const lines = String(raw || "").replace(/\r/g, "").split("\n");
        const out = [];
        const seen = new Set();
        for (const line of lines) {
            const row = parseBulkInputLine(line);
            if (!row) continue;
            const lk = row.keyword.toLowerCase();
            if (seen.has(lk)) continue;
            seen.add(lk);
            out.push(row);
        }
        return out;
    };
    const _rowFromParsed = (parsed, extra = {}) => ({
        id: _bulkRowId(),
        keyword: parsed.keyword,
        search_volume: extra.search_volume != null ? String(extra.search_volume) : "",
        content_type: extra.content_type || "",
        competitor_url: extra.competitor_url || "",
        custom_title: parsed.custom_title || "",
        custom_description: parsed.custom_description || "",
        custom_outline: parsed.custom_outline || "",
        detailsOpen: !!(parsed.custom_title || parsed.custom_description || parsed.custom_outline || extra.competitor_url),
    });
    const bulkRowToApiItem = (row) => ({
        keyword: row.keyword,
        custom_title: row.custom_title || "",
        custom_description: row.custom_description || "",
        custom_outline: row.custom_outline || "",
        search_volume: row.search_volume ? parseInt(row.search_volume, 10) || 0 : 0,
        content_type: row.content_type || "",
        competitor_url: row.competitor_url || "",
    });
    const mergeBulkItems = () => bulkKeywordRows.map(bulkRowToApiItem);
    const parseBulkKeywordsText = (raw) => parseBulkItemsText(raw).map((x) => x.keyword);
    const mergeBulkKeywords = () => mergeBulkItems().map((x) => x.keyword);
    const _findBulkRow = (id) => bulkKeywordRows.find((r) => r.id === id);
    const renderBulkKeywordList = () => {
        if (!bulkKeywordList) return;
        bulkKeywordList.querySelectorAll(".bulk-kw-card").forEach((el) => el.remove());
        if (!bulkKeywordRows.length) {
            if (bulkKeywordListEmpty) {
                bulkKeywordListEmpty.hidden = false;
                bulkKeywordList.appendChild(bulkKeywordListEmpty);
            }
            return;
        }
        if (bulkKeywordListEmpty) bulkKeywordListEmpty.hidden = true;
        bulkKeywordRows.forEach((row) => {
            const card = document.createElement("motion");
            card.className = `bulk-kw-card${row.detailsOpen ? " is-open" : ""}`;
            card.dataset.id = row.id;
            const main = document.createElement("div");
            main.className = "bulk-kw-row-main";
            const kwEl = document.createElement("div");
            kwEl.className = "bulk-kw-keyword";
            kwEl.title = row.keyword;
            kwEl.textContent = row.keyword;
            const volIn = document.createElement("input");
            volIn.type = "number";
            volIn.min = "0";
            volIn.placeholder = "Volume";
            volIn.value = row.search_volume || "";
            volIn.dataset.field = "search_volume";
            const typeSel = document.createElement("select");
            typeSel.dataset.field = "content_type";
            BULK_CONTENT_TYPES.forEach((opt) => {
                const o = document.createElement("option");
                o.value = opt.value;
                o.textContent = opt.label;
                if (opt.value === row.content_type) o.selected = true;
                typeSel.appendChild(o);
            });
            const btnToggle = document.createElement("button");
            btnToggle.type = "button";
            btnToggle.className = "btn secondary btn-bulk-toggle";
            btnToggle.textContent = row.detailsOpen ? "Ẩn" : "Chi tiết";
            const btnRemove = document.createElement("button");
            btnRemove.type = "button";
            btnRemove.className = "btn secondary btn-bulk-remove";
            btnRemove.textContent = "×";
            btnRemove.title = "Xóa";
            main.appendChild(kwEl);
            main.appendChild(volIn);
            main.appendChild(typeSel);
            main.appendChild(btnToggle);
            main.appendChild(btnRemove);
            const details = document.createElement("div");
            details.className = "bulk-kw-details";
            const urlGrid = document.createElement("div");
            urlGrid.className = "bulk-kw-details-grid";
            const urlWrap = document.createElement("div");
            urlWrap.className = "field-mini";
            urlWrap.innerHTML = "<label>URL đối thủ (lấy outline)</label>";
            const urlIn = document.createElement("input");
            urlIn.type = "url";
            urlIn.placeholder = "https://domain-doi-thu.com/bai-viet";
            urlIn.value = row.competitor_url || "";
            urlIn.dataset.field = "competitor_url";
            urlWrap.appendChild(urlIn);
            const btnOutline = document.createElement("button");
            btnOutline.type = "button";
            btnOutline.className = "btn secondary";
            btnOutline.textContent = "Lấy outline";
            urlGrid.appendChild(urlWrap);
            urlGrid.appendChild(btnOutline);
            const mkField = (label, field, tag, ph) => {
                const w = document.createElement("div");
                w.className = "field-mini";
                const lb = document.createElement("label");
                lb.textContent = label;
                const el = document.createElement(tag);
                el.dataset.field = field;
                el.placeholder = ph;
                if (field === "custom_outline") {
                    el.value = row.custom_outline || "";
                } else {
                    el.value = row[field] || "";
                }
                w.appendChild(lb);
                w.appendChild(el);
                return w;
            };
            details.appendChild(urlGrid);
            details.appendChild(mkField("Title (SEO)", "custom_title", "input", "Tiêu đề tùy chỉnh"));
            details.appendChild(mkField("Meta description", "custom_description", "input", "Mô tả meta 140–160 ký tự"));
            details.appendChild(mkField("Outline", "custom_outline", "textarea", "H2: …; H2: … hoặc markdown # / ##"));
            card.appendChild(main);
            card.appendChild(details);
            const syncField = (el) => {
                const f = el.dataset.field;
                if (!f || !_findBulkRow(row.id)) return;
                const r = _findBulkRow(row.id);
                if (f === "search_volume") r.search_volume = el.value;
                else r[f] = el.value;
            };
            volIn.addEventListener("input", () => syncField(volIn));
            typeSel.addEventListener("change", () => syncField(typeSel));
            urlIn.addEventListener("input", () => syncField(urlIn));
            details.querySelectorAll("[data-field]").forEach((el) => {
                el.addEventListener("input", () => syncField(el));
                el.addEventListener("change", () => syncField(el));
            });
            btnToggle.addEventListener("click", () => {
                const r = _findBulkRow(row.id);
                if (!r) return;
                r.detailsOpen = !r.detailsOpen;
                renderBulkKeywordList();
            });
            btnRemove.addEventListener("click", () => {
                bulkKeywordRows = bulkKeywordRows.filter((x) => x.id !== row.id);
                renderBulkKeywordList();
                updateBulkKwCount();
            });
            btnOutline.addEventListener("click", async () => {
                const r = _findBulkRow(row.id);
                if (!r) return;
                const url = String(r.competitor_url || urlIn.value || "").trim();
                if (!url) {
                    appendBulkLog(`[${r.keyword}] Chưa có URL đối thủ.`);
                    return;
                }
                r.competitor_url = url;
                btnOutline.disabled = true;
                btnOutline.textContent = "Đang lấy…";
                try {
                    const res = await fetch(`/content-ai/outline-reference?ts=${Date.now()}`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ competitor_url: url }),
                    });
                    const data = await res.json().catch(() => ({}));
                    if (!res.ok) throw new Error((data && data.detail) ? data.detail : "Không lấy outline");
                    r.custom_outline = (data.outline || "").trim();
                    r.detailsOpen = true;
                    renderBulkKeywordList();
                    appendBulkLog(`[${r.keyword}] Đã lấy ${data.count || 0} heading outline.`);
                } catch (e) {
                    appendBulkLog(`[${r.keyword}] ${String(e.message || e)}`);
                } finally {
                    btnOutline.disabled = false;
                    btnOutline.textContent = "Lấy outline";
                }
            });
            bulkKeywordList.appendChild(card);
        });
    };
    const fetchBulkSearchVolume = async (keyword) => {
        try {
            const res = await fetch("/keywords/volume/batch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ keywords: [keyword], country: "vn", language: "vi" }),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) return null;
            const row = data && data[keyword];
            if (row && row.search_volume != null) return row.search_volume;
        } catch (_) {}
        return null;
    };
    const addBulkKeywordsFromParsed = async (parsedList, { fetchVolume = true } = {}) => {
        let added = 0;
        for (const parsed of parsedList) {
            const lk = parsed.keyword.toLowerCase();
            if (bulkKeywordRows.some((r) => r.keyword.toLowerCase() === lk)) continue;
            const row = _rowFromParsed(parsed);
            bulkKeywordRows.push(row);
            added += 1;
            if (fetchVolume) {
                const vol = await fetchBulkSearchVolume(parsed.keyword);
                if (vol != null) row.search_volume = String(vol);
            }
        }
        if (added) {
            renderBulkKeywordList();
            updateBulkKwCount();
        }
        return added;
    };
    const addBulkKeywordFromInput = async () => {
        const raw = bulkAddKeywordInput ? bulkAddKeywordInput.value : "";
        const parsed = parseBulkInputLine(raw);
        if (!parsed) {
            appendBulkLog("Từ khóa trống.");
            return;
        }
        const n = await addBulkKeywordsFromParsed([parsed], { fetchVolume: true });
        if (!n) {
            appendBulkLog(`Từ khóa «${parsed.keyword}» đã có trong danh sách.`);
            return;
        }
        if (bulkAddKeywordInput) bulkAddKeywordInput.value = "";
    };
    const importBulkTextToList = async () => {
        const quick = parseBulkItemsText(bulkQuickInput ? bulkQuickInput.value : "");
        const plain = parseBulkItemsText(bulkKeywordsText ? bulkKeywordsText.value : "");
        const all = [...quick, ...plain];
        if (!all.length) {
            appendBulkLog("Không có dòng để import.");
            return;
        }
        const n = await addBulkKeywordsFromParsed(all, { fetchVolume: true });
        appendBulkLog(`Đã thêm ${n} từ khóa vào danh sách.`);
        if (bulkKeywordsText) bulkKeywordsText.value = "";
        if (bulkQuickInput) bulkQuickInput.value = "";
    };
    const updateBulkKwCount = () => {
        const items = mergeBulkItems();
        const n = items.length;
        const customN = items.filter((x) => x.custom_title || x.custom_description || x.custom_outline).length;
        if (bulkKwCount) {
            bulkKwCount.textContent = customN
                ? `${n} từ khóa (${customN} có cấu hình chi tiết)`
                : `${n} từ khóa`;
        }
        return n;
    };
'''

new_block = new_block.replace('document.createElement("motion")', 'document.createElement("div")')

text = text[:i0] + new_block + text[i1:]
p.write_text(text, encoding="utf-8")
print("JS OK")
