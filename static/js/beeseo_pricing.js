/**
 * BeeSEO Pricing modal — static plan data from product sheet (6-month PayOS VND baseline).
 * Exposes window.openBeeSEOPricingModal() and syncs global user pill when present.
 */
(function () {
    const VND_PER_USD = 25000;

    const DURATIONS = [
        { id: "m6", label: "6 months", months: 6, factor: 1 },
        { id: "y1", label: "1 year", months: 12, factor: 1.85 },
        { id: "y2", label: "2 years", months: 24, factor: 3.35 },
        { id: "life", label: "Lifetime", months: null, factor: null },
    ];

    const BASE_VND_6M = {
        basic: 1500000,
        pro: 2490000,
        agency: 4490000,
        unlimited: 6990000,
    };

    const LIFETIME_VND = {
        basic: 12500000,
        pro: 20500000,
        agency: 37000000,
        unlimited: 58000000,
    };

    const PLANS = [
        {
            id: "basic",
            name: "Basic",
            popular: false,
            articles: "50 articles/month",
            projects: "3 projects",
            devices: "2 devices",
            gsc: false,
        },
        {
            id: "pro",
            name: "Pro",
            popular: true,
            articles: "100 articles/month",
            projects: "10 projects",
            devices: "3 devices",
            gsc: true,
        },
        {
            id: "agency",
            name: "Agency",
            popular: false,
            articles: "500 articles/month",
            projects: "50 projects",
            devices: "4 devices",
            gsc: true,
        },
        {
            id: "unlimited",
            name: "Unlimited",
            popular: false,
            articles: "Unlimited articles/month",
            projects: "Unlimited projects",
            devices: "5 devices",
            gsc: true,
        },
    ];

    const FEATS = [
        { key: "ai_write", label: "AI article writing" },
        { key: "ai_image", label: "AI image generation" },
        { key: "wp_pub", label: "WordPress publishing" },
        { key: "internal_links", label: "Internal Links" },
        { key: "knowledge", label: "knowledge_base" },
        { key: "gsc", label: "Google Search Console" },
    ];

    let state = { duration: "m6", payment: "payos" };

    function formatVnd(n) {
        const x = Math.round(Number(n) || 0);
        return x.toLocaleString("vi-VN") + "đ";
    }

    function formatUsd(n) {
        const usd = (Number(n) || 0) / VND_PER_USD;
        const rounded = Math.max(1, Math.round(usd));
        return "$" + rounded.toLocaleString("en-US");
    }

    function priceForPlan(planId) {
        const base = BASE_VND_6M[planId];
        if (state.duration === "life") return LIFETIME_VND[planId];
        const dur = DURATIONS.find((d) => d.id === state.duration);
        const f = dur && dur.factor != null ? dur.factor : 1;
        return Math.round(base * f);
    }

    function perMonthVnd(total, months) {
        if (!months) return null;
        return Math.round(total / months);
    }

    function renderGrid() {
        const grid = document.getElementById("beeseoPricingGrid");
        if (!grid) return;
        const dur = DURATIONS.find((d) => d.id === state.duration);
        const months = dur ? dur.months : null;
        const payLabel = state.payment === "paypal" ? "USD" : "VND";

        grid.innerHTML = PLANS.map((p) => {
            const totalVnd = priceForPlan(p.id);
            const displayMain =
                state.payment === "paypal" ? formatUsd(totalVnd) : formatVnd(totalVnd) + " / " + (dur ? dur.label : "Lifetime");
            let perLine = "";
            if (state.payment === "payos" && months) {
                const pm = perMonthVnd(totalVnd, months);
                perLine = `(~ ${formatVnd(pm)}/month)`;
            } else if (state.payment === "paypal" && months) {
                const totalUsd = totalVnd / VND_PER_USD;
                const pmUsd = totalUsd / months;
                perLine = `(~ $${Math.max(1, Math.round(pmUsd))}/month)`;
            } else if (state.duration === "life") {
                perLine = state.payment === "paypal" ? "One-time payment" : "Thanh toán một lần";
            }
            const featHtml = FEATS.map((f) => {
                const on = f.key === "gsc" ? p.gsc : true;
                const mark = on ? '<span class="ok">✓</span>' : '<span class="no">✗</span>';
                return `<li>${mark}<span>${f.label}</span></li>`;
            }).join("");
            const pop = p.popular ? '<div class="beeseo-plan-badge">Most popular</div>' : "";
            return (
                `<article class="beeseo-plan-card${p.popular ? " is-popular" : ""}" data-plan="${p.id}">` +
                pop +
                `<div class="beeseo-plan-name">${p.name}</div>` +
                `<div class="beeseo-plan-price">${displayMain}</div>` +
                (perLine ? `<div class="beeseo-plan-per">${perLine}</div>` : "") +
                `<div class="beeseo-plan-meta">` +
                `<div><strong>${p.articles}</strong></div>` +
                `<div><strong>${p.projects}</strong></div>` +
                `<div><strong>${p.devices}</strong></div>` +
                `</div>` +
                `<ul class="beeseo-plan-features">${featHtml}</ul>` +
                `<button type="button" class="beeseo-plan-buy" data-buy-plan="${p.id}">Mua ngay</button>` +
                `</article>`
            );
        }).join("");

        grid.querySelectorAll("[data-buy-plan]").forEach((btn) => {
            btn.addEventListener("click", () => {
                const id = btn.getAttribute("data-buy-plan");
                const plan = PLANS.find((x) => x.id === id);
                window.alert(
                    "Gói: " +
                        (plan ? plan.name : id) +
                        " — Thanh toán PayOS / PayPal sẽ được kết nối trong bản cập nhật tới. Liên hệ admin để kích hoạt thủ công.",
                );
            });
        });
    }

    function syncToggles() {
        document.querySelectorAll(".beeseo-dur-btn").forEach((b) => {
            b.classList.toggle("is-active", b.getAttribute("data-dur") === state.duration);
        });
        document.querySelectorAll(".beeseo-pay-btn").forEach((b) => {
            b.classList.toggle("is-active", b.getAttribute("data-pay") === state.payment);
        });
    }

    function openModal() {
        const bd = document.getElementById("beeseoPricingBackdrop");
        if (!bd) return;
        syncToggles();
        renderGrid();
        bd.classList.add("is-open");
        document.body.style.overflow = "hidden";
    }

    function closeModal() {
        const bd = document.getElementById("beeseoPricingBackdrop");
        if (!bd) return;
        bd.classList.remove("is-open");
        document.body.style.overflow = "";
    }

    function wireModal() {
        const bd = document.getElementById("beeseoPricingBackdrop");
        if (!bd) return;
        const closeBtn = document.getElementById("beeseoPricingClose");
        if (closeBtn) closeBtn.addEventListener("click", closeModal);
        bd.addEventListener("click", (e) => {
            if (e.target === bd) closeModal();
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && bd.classList.contains("is-open")) closeModal();
        });
        document.querySelectorAll(".beeseo-dur-btn").forEach((b) => {
            b.addEventListener("click", () => {
                state.duration = b.getAttribute("data-dur") || "m6";
                syncToggles();
                renderGrid();
            });
        });
        document.querySelectorAll(".beeseo-pay-btn").forEach((b) => {
            b.addEventListener("click", () => {
                state.payment = b.getAttribute("data-pay") || "payos";
                syncToggles();
                renderGrid();
            });
        });
        document.querySelectorAll("[data-beeseo-pricing-open]").forEach((el) => {
            el.addEventListener("click", (ev) => {
                ev.preventDefault();
                openModal();
            });
        });
    }

    function syncGlobalDock() {
        const wrap = document.getElementById("globalUserDockWrap");
        if (!wrap || wrap.hasAttribute("hidden")) return;
        const label = document.getElementById("globalUserDockLabel");
        const av = document.getElementById("globalUserDockAvatar");
        if (!label || !av) return;
        let token = "";
        try {
            token = sessionStorage.getItem("seo_token") || "";
        } catch (_) {}
        if (!token) {
            label.textContent = "Chưa đăng nhập";
            av.textContent = "?";
            av.classList.add("is-guest");
            return;
        }
        fetch("/auth/me", { headers: { Authorization: "Bearer " + token } })
            .then((r) => (r.ok ? r.json() : null))
            .then((d) => {
                if (!d || !d.email) {
                    label.textContent = "Đã đăng nhập";
                    av.textContent = "U";
                    av.classList.remove("is-guest");
                    return;
                }
                label.textContent = d.email;
                av.textContent = String(d.email).trim().charAt(0).toUpperCase() || "U";
                av.classList.remove("is-guest");
            })
            .catch(() => {
                label.textContent = "Chưa đăng nhập";
                av.textContent = "?";
                av.classList.add("is-guest");
            });
    }

    function wireGlobalDock() {
        const dismiss = document.getElementById("globalUserDockDismiss");
        const wrap = document.getElementById("globalUserDockWrap");
        const pill = document.getElementById("globalUserDockPill");
        if (dismiss && wrap) {
            dismiss.addEventListener("click", (e) => {
                e.stopPropagation();
                try {
                    sessionStorage.setItem("beeseo_global_dock_hidden", "1");
                } catch (_) {}
                wrap.hidden = true;
            });
        }
        if (pill) {
            pill.addEventListener("click", (e) => {
                if (e.target.closest("#globalUserDockDismiss")) return;
                window.location.href = "/settings#account";
            });
            pill.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    if (!e.target.closest("#globalUserDockDismiss")) window.location.href = "/settings#account";
                }
            });
        }
        syncGlobalDock();
    }

    window.openBeeSEOPricingModal = openModal;
    window.closeBeeSEOPricingModal = closeModal;
    window.refreshBeeSEOGlobalDock = syncGlobalDock;

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    function init() {
        const wrap = document.getElementById("globalUserDockWrap");
        const dockMode = document.body ? document.body.getAttribute("data-user-dock") : "";
        if (wrap && (dockMode === "sidebar" || dockMode === "hidden")) {
            wrap.remove();
        } else if (wrap && dockMode === "upgrade-only") {
            wrap.classList.add("is-upgrade-only");
            const pill = document.getElementById("globalUserDockPill");
            if (pill) pill.remove();
        }
        wireModal();
        wireGlobalDock();
        const w2 = document.getElementById("globalUserDockWrap");
        if (w2) {
            let hid = false;
            try {
                hid = sessionStorage.getItem("beeseo_global_dock_hidden") === "1";
            } catch (_) {}
            if (hid) w2.hidden = true;
        }
    }
})();
