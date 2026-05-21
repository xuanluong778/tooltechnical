/**
 * Show "Quản trị viên" / "Administrator" nav link only when /auth/me reports role=admin.
 */
(function () {
    const TOKEN_KEY = "seo_token";

    function readCookieToken() {
        const m = document.cookie.match(/(?:^|;\s*)seo_token=([^;]*)/);
        return m ? decodeURIComponent(m[1].replace(/\+/g, " ")).trim() : "";
    }

    function token() {
        try {
            let t = (sessionStorage.getItem(TOKEN_KEY) || "").trim();
            if (!t) {
                t = readCookieToken();
                if (t) sessionStorage.setItem(TOKEN_KEY, t);
            }
            return t;
        } catch (_) {
            return readCookieToken();
        }
    }

    function applyNavI18n() {
        if (window.BeeSeoI18n && typeof window.BeeSeoI18n.apply === "function") {
            window.BeeSeoI18n.apply(window.BeeSeoI18n.readLang());
        }
    }

    function revealAdminLinks() {
        document.querySelectorAll("[data-nav-admin]").forEach((el) => {
            el.hidden = false;
            el.removeAttribute("hidden");
            el.classList.remove("hidden");
        });
        applyNavI18n();
    }

    function hideAdminLinks() {
        document.querySelectorAll("[data-nav-admin]").forEach((el) => {
            el.hidden = true;
            el.setAttribute("hidden", "");
        });
    }

    function run() {
        hideAdminLinks();
        const t = token();
        if (!t) return;
        fetch("/auth/me", { credentials: "same-origin", headers: { Authorization: "Bearer " + t } })
            .then((r) => (r.ok ? r.json() : null))
            .then((u) => {
                if (u && String(u.role || "").toLowerCase() === "admin") revealAdminLinks();
            })
            .catch(() => {});
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", run);
    } else {
        run();
    }

    window.addEventListener("storage", (e) => {
        if (e.key === "beeseo_system_prefs_v1") applyNavI18n();
    });

    window.refreshBeeSEOAdminNav = run;

    window.addEventListener("beeseo-auth-change", (e) => {
        if (e.detail && e.detail.loggedIn === false) hideAdminLinks();
        else run();
    });
})();
