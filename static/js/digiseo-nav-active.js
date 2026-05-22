/**
 * Top nav: highlight tab trùng trang hiện tại (mọi layout: nav-strip, div.nav, Tailwind flex).
 */
(function () {
    var TOP_NAV_LINK =
        '[aria-label="Menu chính"] > a, ' +
        '.nav-strip .nav > a, .nav-strip nav > a, ' +
        '.header-inner .main-nav > a, ' +
        '.report-top > a, p.report-top > a, ' +
        '.pricing-page-nav .inner > a';

    function normPath(p) {
        if (!p) return "/";
        var x = String(p).split("?")[0].split("#")[0].replace(/\/+$/, "");
        return x || "/";
    }

    function normHref(href) {
        if (!href || href.indexOf("http") === 0 || href.indexOf("#") === 0) return "";
        return normPath(href);
    }

    function pathMatches(linkPath, pagePath) {
        if (!linkPath || !pagePath) return false;
        if (linkPath === pagePath) return true;

        if (linkPath === "/") {
            return pagePath === "/" || pagePath === "";
        }

        if (linkPath === "/report") {
            return pagePath === "/report" || pagePath.indexOf("/report/") === 0;
        }

        if (linkPath === "/tool/seo-score") {
            return pagePath === "/tool/seo-score" || pagePath.indexOf("/tool/seo-score/") === 0;
        }

        if (linkPath === "/tool") {
            return pagePath === "/tool";
        }

        if (linkPath === "/keywords/tools/research" || linkPath === "/keywords") {
            return pagePath === "/keywords" || pagePath.indexOf("/keywords/") === 0;
        }

        if (linkPath === "/content-ai") {
            return pagePath === "/content-ai" || pagePath.indexOf("/content-ai/") === 0;
        }

        if (linkPath === "/schema") {
            return pagePath === "/schema" || pagePath.indexOf("/schema/") === 0;
        }

        if (linkPath === "/pricing") {
            return pagePath === "/pricing";
        }

        if (linkPath === "/settings") {
            return pagePath === "/settings" || pagePath.indexOf("/settings/") === 0;
        }

        if (linkPath === "/admin") {
            return pagePath === "/admin" || pagePath.indexOf("/admin/") === 0;
        }

        return pagePath.indexOf(linkPath + "/") === 0;
    }

    function topNavLinks() {
        return Array.prototype.slice.call(document.querySelectorAll(TOP_NAV_LINK));
    }

    function markTopNavActive() {
        var pagePath = normPath(window.location && window.location.pathname);
        var links = topNavLinks();
        links.forEach(function (a) {
            a.classList.remove("active", "is-active");
            a.removeAttribute("aria-current");
        });
        links.forEach(function (a) {
            var linkPath = normHref(a.getAttribute("href") || "");
            if (!linkPath || linkPath === "/") return;
            if (pathMatches(linkPath, pagePath)) {
                a.classList.add("active");
                a.setAttribute("aria-current", "page");
            }
        });
    }

    function bindTopNavClicks() {
        topNavLinks().forEach(function (a) {
            if (a.dataset.digiseoNavBound) return;
            a.dataset.digiseoNavBound = "1";
            a.addEventListener("click", function () {
                if (a.target === "_blank" || a.hasAttribute("download")) return;
                var linkPath = normHref(a.getAttribute("href") || "");
                if (!linkPath || linkPath === "/") return;
                topNavLinks().forEach(function (x) {
                    x.classList.remove("active", "is-active");
                    x.removeAttribute("aria-current");
                });
                a.classList.add("active");
                a.setAttribute("aria-current", "page");
            });
        });
    }

    function init() {
        markTopNavActive();
        bindTopNavClicks();
        if (window.DigiSeoI18n && typeof window.DigiSeoI18n.init === "function") {
            window.addEventListener("digiseo:i18n-applied", markTopNavActive);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
    window.setTimeout(markTopNavActive, 0);
    window.addEventListener("pageshow", markTopNavActive);
    window.addEventListener("popstate", markTopNavActive);
    window.markdigiseoTopNavActive = markTopNavActive;
})();
