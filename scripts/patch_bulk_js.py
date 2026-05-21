from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates/content_ai.html"
text = p.read_text(encoding="utf-8")

old = """    const bulkKeywordsText = byId("bulkKeywordsText");
    const bulkKeywordsFile = byId("bulkKeywordsFile");
    const bulkKwCount = byId("bulkKwCount");
    const bulkJobLog = byId("bulkJobLog");
    const bulkJobProgress = byId("bulkJobProgress");
    const bulkJobProgressFill = byId("bulkJobProgressFill");
    const bulkJobStatus = byId("bulkJobStatus");
    const bulkJobPct = byId("bulkJobPct");
    const bulkJobItems = byId("bulkJobItems");
    const parseBulkKeywordsText = (raw) => {
        const lines = String(raw || "").replace(/\\r/g, "").split("\\n");
        const out = [];
        const seen = new Set();
        for (const line of lines) {
            let k = String(line || "").trim();
            if (!k) continue;
            if (k.includes(",")) k = k.split(",")[0].trim();
            if (k.startsWith('"') && k.endsWith('"')) k = k.slice(1, -1).trim();
            const lk = k.toLowerCase();
            if (!k || seen.has(lk)) continue;
            seen.add(lk);
            out.push(k);
        }
        return out;
    };
    const mergeBulkKeywords = () => parseBulkKeywordsText(bulkKeywordsText ? bulkKeywordsText.value : "");
    const updateBulkKwCount = () => {
        const n = mergeBulkKeywords().length;
        if (bulkKwCount) bulkKwCount.textContent = `${n} từ khóa`;
        return n;
    };"""

new = """    const bulkKeywordsText = byId("bulkKeywordsText");
    const bulkQuickInput = byId("bulkQuickInput");
    const bulkKeywordsFile = byId("bulkKeywordsFile");
    const bulkKwCount = byId("bulkKwCount");
    const bulkJobLog = byId("bulkJobLog");
    const bulkJobProgress = byId("bulkJobProgress");
    const bulkJobProgressFill = byId("bulkJobProgressFill");
    const bulkJobStatus = byId("bulkJobStatus");
    const bulkJobPct = byId("bulkJobPct");
    const bulkJobItems = byId("bulkJobItems");
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
        } else if (raw.includes(",") && !/\\bH[1-3]\\s*:/i.test(raw)) {
            keyword = raw.split(",")[0].trim();
        } else {
            keyword = raw;
        }
        keyword = keyword.replace(/\\s+/g, " ").trim();
        if (!keyword) return null;
        return { keyword, custom_title, custom_description, custom_outline };
    };
    const parseBulkItemsText = (raw) => {
        const lines = String(raw || "").replace(/\\r/g, "").split("\\n");
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
    const mergeBulkItems = () => {
        const quick = parseBulkItemsText(bulkQuickInput ? bulkQuickInput.value : "");
        const plain = parseBulkItemsText(bulkKeywordsText ? bulkKeywordsText.value : "");
        const map = new Map();
        [...quick, ...plain].forEach((row) => {
            const lk = row.keyword.toLowerCase();
            const prev = map.get(lk);
            if (!prev) {
                map.set(lk, { ...row });
                return;
            }
            map.set(lk, {
                keyword: row.keyword,
                custom_title: row.custom_title || prev.custom_title || "",
                custom_description: row.custom_description || prev.custom_description || "",
                custom_outline: row.custom_outline || prev.custom_outline || "",
            });
        });
        return Array.from(map.values());
    };
    const parseBulkKeywordsText = (raw) => parseBulkItemsText(raw).map((x) => x.keyword);
    const mergeBulkKeywords = () => mergeBulkItems().map((x) => x.keyword);
    const updateBulkKwCount = () => {
        const items = mergeBulkItems();
        const n = items.length;
        const customN = items.filter((x) => x.custom_title || x.custom_description || x.custom_outline).length;
        if (bulkKwCount) {
            bulkKwCount.textContent = customN
                ? `${n} dòng (${customN} có title/description/outline tùy chỉnh)`
                : `${n} dòng`;
        }
        return n;
    };"""

if old not in text:
    raise SystemExit("JS block not found")
text = text.replace(old, new, 1)

text = text.replace(
    'const ids = ["bulkTargetWebsite", "bulkSecondaryKeywords", "bulkKeywordsText"];',
    'const ids = ["bulkTargetWebsite", "bulkSecondaryKeywords", "bulkQuickInput", "bulkKeywordsText"];',
    1,
)

text = text.replace(
    """            const keywords = mergeBulkKeywords();
            if (!keywords.length) {
                appendBulkLog("Chưa có từ khóa.");
                return;
            }""",
    """            const bulkItems = mergeBulkItems();
            if (!bulkItems.length) {
                appendBulkLog("Chưa có từ khóa.");
                return;
            }
            const keywords = bulkItems.map((x) => x.keyword);""",
    1,
)

text = text.replace(
    'body: JSON.stringify({ keywords, target_website, target_word_count, secondary_keywords }),',
    'body: JSON.stringify({ keywords, items: bulkItems, target_website, target_word_count, secondary_keywords }),',
    1,
)

if "bulkQuickInput" not in text.split("addEventListener(\"input\", updateBulkKwCount)")[0][-500:]:
    text = text.replace(
        "if (bulkKeywordsText) bulkKeywordsText.addEventListener(\"input\", updateBulkKwCount);",
        "if (bulkKeywordsText) bulkKeywordsText.addEventListener(\"input\", updateBulkKwCount);\n    if (bulkQuickInput) bulkQuickInput.addEventListener(\"input\", updateBulkKwCount);",
        1,
    )

p.write_text(text, encoding="utf-8")
print("OK")
