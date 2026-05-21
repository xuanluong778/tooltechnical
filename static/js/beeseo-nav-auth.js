/**
 * Top-right Login / Logout for pages using nav-strip (settings, content-ai, report, …).
 * Home (/), Technical tool sidebar: use their own controls — bar not injected.
 */
(function () {
    const TOKEN_KEY = "seo_token";

    function readCookieToken() {
        const m = document.cookie.match(/(?:^|;\s*)seo_token=([^;]*)/);
        return m ? decodeURIComponent(m[1].replace(/\+/g, " ")).trim() : "";
    }

    function getToken() {
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

    function shouldInjectBar() {
        const mode = (document.body && document.body.getAttribute("data-user-dock")) || "";
        if (mode === "sidebar") return false;
        if (document.body && document.body.classList.contains("page-tool")) return false;
        if (document.getElementById("btnOpenLogin") && document.querySelector(".header-actions")) return false;
        return true;
    }

    function hideAdminNavLinks() {
        document.querySelectorAll("[data-nav-admin]").forEach((el) => {
            el.hidden = true;
            el.setAttribute("hidden", "");
            el.classList.add("hidden");
        });
    }

    function applyI18n(el) {
        if (!el || !window.BeeSeoI18n) return;
        const key = el.getAttribute("data-i18n");
        if (!key) return;
        el.textContent = window.BeeSeoI18n.t(window.BeeSeoI18n.readLang(), key);
    }

    function ensureBar() {
        if (!shouldInjectBar()) return null;
        let bar = document.getElementById("beeseoNavAuthBar");
        if (bar) return bar;

        bar = document.createElement("div");
        bar.id = "beeseoNavAuthBar";
        bar.className = "beeseo-nav-auth-bar";
        bar.setAttribute("aria-label", "Account");

        const emailSpan = document.createElement("span");
        emailSpan.id = "beeseoNavAuthEmail";
        emailSpan.className = "beeseo-nav-auth-email";
        emailSpan.hidden = true;

        const btnLogin = document.createElement("button");
        btnLogin.type = "button";
        btnLogin.id = "beeseoNavLogin";
        btnLogin.className = "beeseo-nav-auth-btn is-login";
        btnLogin.setAttribute("data-i18n", "auth.login");
        btnLogin.textContent = "Đăng nhập";

        const btnLogout = document.createElement("button");
        btnLogout.type = "button";
        btnLogout.id = "beeseoNavLogout";
        btnLogout.className = "beeseo-nav-auth-btn is-logout";
        btnLogout.setAttribute("data-i18n", "auth.logout");
        btnLogout.textContent = "Đăng xuất";
        btnLogout.hidden = true;

        bar.appendChild(emailSpan);
        bar.appendChild(btnLogin);
        bar.appendChild(btnLogout);
        document.body.appendChild(bar);

        btnLogin.addEventListener("click", () => {
            const local = document.getElementById("btnOpenLogin");
            if (local) {
                local.click();
                return;
            }
            window.location.href = "/tool";
        });

        btnLogout.addEventListener("click", () => {
            if (typeof window.beeSEOLogout === "function") {
                window.beeSEOLogout();
                return;
            }
            window.beeSEOClearSession();
            syncBar();
        });

        applyI18n(btnLogin);
        applyI18n(btnLogout);
        return bar;
    }

    function syncBar() {
        const bar = ensureBar();
        if (!bar) return;

        const btnLogin = document.getElementById("beeseoNavLogin");
        const btnLogout = document.getElementById("beeseoNavLogout");
        const emailSpan = document.getElementById("beeseoNavAuthEmail");
        if (!btnLogin || !btnLogout) return;

        const t = getToken();
        if (!t) {
            btnLogin.hidden = false;
            btnLogout.hidden = true;
            if (emailSpan) emailSpan.hidden = true;
            hideAdminNavLinks();
            return;
        }

        fetch("/auth/me", { credentials: "same-origin", headers: { Authorization: "Bearer " + t } })
            .then((r) => (r.ok ? r.json() : null))
            .then((u) => {
                if (!u || !u.email) {
                    btnLogin.hidden = false;
                    btnLogout.hidden = true;
                    if (emailSpan) emailSpan.hidden = true;
                    hideAdminNavLinks();
                    return;
                }
                btnLogin.hidden = true;
                btnLogout.hidden = false;
                if (emailSpan) {
                    emailSpan.textContent = u.email;
                    emailSpan.hidden = false;
                }
                if (typeof window.refreshBeeSEOAdminNav === "function") {
                    window.refreshBeeSEOAdminNav();
                }
            })
            .catch(() => {
                btnLogin.hidden = false;
                btnLogout.hidden = true;
                if (emailSpan) emailSpan.hidden = true;
                hideAdminNavLinks();
            });
    }

    window.beeSEOClearSession = function beeSEOClearSession() {
        try {
            sessionStorage.removeItem(TOKEN_KEY);
        } catch (_) {}
        document.cookie = "seo_token=; path=/; max-age=0; SameSite=Lax";
        hideAdminNavLinks();
        if (typeof window.refreshBeeSEOGlobalDock === "function") {
            window.refreshBeeSEOGlobalDock();
        }
        window.dispatchEvent(new CustomEvent("beeseo-auth-change", { detail: { loggedIn: false } }));
    };

    window.beeSEOLogout = function beeSEOLogout() {
        window.beeSEOClearSession();
        syncBar();
    };

    window.refreshBeeSEONavAuth = syncBar;

    function init() {
        ensureBar();
        syncBar();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    window.addEventListener("beeseo-auth-change", syncBar);
    window.addEventListener("storage", (e) => {
        if (e.key === TOKEN_KEY || e.key === "beeseo_system_prefs_v1") syncBar();
    });
})();
