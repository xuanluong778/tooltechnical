/**
 * Top nav: mark current page active + brief highlight on click (before navigation).
 */
(function () {
    var TOP_NAV_LINK =
        ".nav-strip .nav > a, .nav-strip nav.nav > a, .nav-strip nav[aria-label=\"Menu chính\"] > a, " +
        "p.report-top > a, .header-inner .main-nav > a, nav[aria-label=\"Menu chính\"] > a";

    function normPath(p) {
        if (!p) return "/";
        var x = p.split("?")[0].split("#")[0].replace(/\/+$/, "");
        return x || "/";
    }

    function normHref(href) {
        if (!href || href.indexOf("http") === 0 || href.indexOf("#") === 0) return "";
        return normPath(href);
    }

    function pathMatches(linkPath, pagePath) {
        if (!linkPath || !pagePath) return false;
        if (linkPath === pagePath) return true;
        if (
            (pagePath === "/keywords" || pagePath.indexOf("/keywords/") === 0) &&
            (linkPath === "/keywords" || linkPath === "/keywords/tools/research")
        ) {
            return true;
        }
        if (pagePath.indexOf("/tool") === 0 && linkPath === "/tool") return pagePath === "/tool";
        if (pagePath === "/tool/seo-score" && linkPath === "/tool/seo-score") return true;
        return false;
    }

    function topNavLinks() {
        return Array.prototype.slice.call(document.querySelectorAll(TOP_NAV_LINK));
    }

    function markTopNavActive() {
        var pagePath = normPath(window.location && window.location.pathname);
        topNavLinks().forEach(function (a) {
            a.classList.remove("active");
            a.removeAttribute("aria-current");
        });
        topNavLinks().forEach(function (a) {
            var linkPath = normHref(a.getAttribute("href") || "");
            if (pathMatches(linkPath, pagePath)) {
                a.classList.add("active");
                a.setAttribute("aria-current", "page");
            }
        });
    }

    function bindTopNavClicks() {
        topNavLinks().forEach(function (a) {
            if (a.dataset.beeseoNavBound) return;
            a.dataset.beeseoNavBound = "1";
            a.addEventListener("click", function () {
                if (a.target === "_blank" || a.hasAttribute("download")) return;
                topNavLinks().forEach(function (x) {
                    x.classList.remove("active");
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
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
    window.addEventListener("pageshow", markTopNavActive);
})();
