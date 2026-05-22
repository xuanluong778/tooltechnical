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
        if (!el || !window.DigiSeoI18n) return;
        const key = el.getAttribute("data-i18n");
        if (!key) return;
        el.textContent = window.DigiSeoI18n.t(window.DigiSeoI18n.readLang(), key);
    }

    function ensureBar() {
        if (!shouldInjectBar()) return null;
        let bar = document.getElementById("digiseoNavAuthBar");
        if (bar) return bar;

        bar = document.createElement("div");
        bar.id = "digiseoNavAuthBar";
        bar.className = "digiseo-nav-auth-bar";
        bar.setAttribute("aria-label", "Account");

        const emailSpan = document.createElement("span");
        emailSpan.id = "digiseoNavAuthEmail";
        emailSpan.className = "digiseo-nav-auth-email";
        emailSpan.hidden = true;

        const btnLogin = document.createElement("button");
        btnLogin.type = "button";
        btnLogin.id = "digiseoNavLogin";
        btnLogin.className = "digiseo-nav-auth-btn is-login";
        btnLogin.setAttribute("data-i18n", "auth.login");
        btnLogin.textContent = "Đăng nhập";

        const btnLogout = document.createElement("button");
        btnLogout.type = "button";
        btnLogout.id = "digiseoNavLogout";
        btnLogout.className = "digiseo-nav-auth-btn is-logout";
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
            if (typeof window.DigiSeoLogout === "function") {
                window.DigiSeoLogout();
                return;
            }
            window.DigiSeoClearSession();
            syncBar();
        });

        applyI18n(btnLogin);
        applyI18n(btnLogout);
        return bar;
    }

    function syncBar() {
        const bar = ensureBar();
        if (!bar) return;

        const btnLogin = document.getElementById("digiseoNavLogin");
        const btnLogout = document.getElementById("digiseoNavLogout");
        const emailSpan = document.getElementById("digiseoNavAuthEmail");
        if (!btnLogin || !btnLogout) return;

        const t = getToken();
        if (!t) {
            bar.hidden = false;
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
                    bar.hidden = false;
                    btnLogin.hidden = false;
                    btnLogout.hidden = true;
                    if (emailSpan) emailSpan.hidden = true;
                    hideAdminNavLinks();
                    return;
                }
                bar.hidden = true;
                btnLogin.hidden = true;
                btnLogout.hidden = true;
                if (emailSpan) emailSpan.hidden = true;
                if (typeof window.refreshDigiSeoAdminNav === "function") {
                    window.refreshDigiSeoAdminNav();
                }
            })
            .catch(() => {
                bar.hidden = false;
                btnLogin.hidden = false;
                btnLogout.hidden = true;
                if (emailSpan) emailSpan.hidden = true;
                hideAdminNavLinks();
            });
    }

    window.DigiSeoClearSession = function digiseoClearSession() {
        try {
            sessionStorage.removeItem(TOKEN_KEY);
        } catch (_) {}
        document.cookie = "seo_token=; path=/; max-age=0; SameSite=Lax";
        hideAdminNavLinks();
        if (typeof window.refreshDigiSeoGlobalDock === "function") {
            window.refreshDigiSeoGlobalDock();
        }
        window.dispatchEvent(new CustomEvent("digiseo-auth-change", { detail: { loggedIn: false } }));
    };

    window.DigiSeoLogout = function digiseoLogout() {
        window.DigiSeoClearSession();
        syncBar();
    };

    window.refreshDigiSeoNavAuth = syncBar;

    function init() {
        ensureBar();
        syncBar();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    window.addEventListener("digiseo-auth-change", syncBar);
    window.addEventListener("storage", (e) => {
        if (e.key === TOKEN_KEY || e.key === "digiseo_system_prefs_v1") syncBar();
    });
})();
