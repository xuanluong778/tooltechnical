/**
 * BeeSEO floating chatbot widget
 */
(function () {
    var ROOT_ID = "beeseoChatbotRoot";
    var AVATAR = "/static/img/beeseo-chatbot-avatar.png";
    var SESSION_KEY = "beeseo_chat_session";
    var FALLBACK_PROMPTS = [
        { id: "pricing", label: "Giá phần mềm bao nhiêu?" },
        { id: "audit", label: "Cách audit website?" },
        { id: "seo_article", label: "Cách tạo bài SEO?" },
        { id: "kb", label: "Cách dùng Knowledge Base?" },
        { id: "api_error", label: "API key bị lỗi thì làm sao?" },
        { id: "wordpress", label: "Cách đăng bài lên WordPress?" },
    ];
    var TAG_DIV = "d" + "iv";
    var history = [];
    var sessionId = "";

    function esc(s) {
        var d = document.createElement(TAG_DIV);
        d.textContent = s;
        return d.innerHTML;
    }

    function formatReply(text) {
        var safe = esc(String(text || ""));
        return safe.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    }

    function getToken() {
        try {
            return sessionStorage.getItem("seo_token") || "";
        } catch (_) {
            return "";
        }
    }

    function getSessionId() {
        if (sessionId) return sessionId;
        try {
            sessionId = sessionStorage.getItem(SESSION_KEY) || "";
            if (!sessionId) {
                sessionId =
                    "s_" +
                    Date.now().toString(36) +
                    "_" +
                    Math.random().toString(36).slice(2, 10);
                sessionStorage.setItem(SESSION_KEY, sessionId);
            }
        } catch (_) {
            sessionId = "s_anon_" + Date.now();
        }
        return sessionId;
    }

    function pagePath() {
        return (window.location && window.location.pathname) || "/";
    }

    function appendMsg(role, text, extraClass) {
        var box = document.getElementById("beeseoChatbotMessages");
        if (!box) return null;
        var row = document.createElement(TAG_DIV);
        row.className =
            "beeseo-chatbot-msg-row" + (role === "user" ? " beeseo-chatbot-msg-row--user" : "");

        if (role !== "user") {
            var img = document.createElement("img");
            img.className = "beeseo-chatbot-msg-ico";
            img.src = AVATAR;
            img.alt = "";
            img.width = 28;
            img.height = 28;
            row.appendChild(img);
        }

        var el = document.createElement(TAG_DIV);
        el.className =
            "beeseo-chatbot-msg beeseo-chatbot-msg--" +
            (role === "user" ? "user" : "bot") +
            (extraClass ? " " + extraClass : "");
        if (role === "user") {
            el.textContent = text;
        } else {
            el.innerHTML = formatReply(text);
        }
        row.appendChild(el);
        box.appendChild(row);
        box.scrollTop = box.scrollHeight;
        return el;
    }

    function setOpen(open) {
        var root = document.getElementById(ROOT_ID);
        if (!root) return;
        root.classList.toggle("is-open", open);
        root.setAttribute("aria-hidden", open ? "false" : "true");
        if (open) {
            var input = document.getElementById("beeseoChatbotInput");
            if (input) setTimeout(function () { input.focus(); }, 120);
        }
    }

    function setSending(busy) {
        var btn = document.getElementById("beeseoChatbotSend");
        var input = document.getElementById("beeseoChatbotInput");
        if (btn) btn.disabled = busy;
        if (input) input.disabled = busy;
        document.querySelectorAll(".beeseo-chatbot-quick-btn").forEach(function (b) {
            b.disabled = busy;
        });
    }

    async function sendMessage(textOverride) {
        var input = document.getElementById("beeseoChatbotInput");
        var text = (textOverride != null ? String(textOverride) : input && input.value) || "";
        text = text.trim();
        if (!text) return;
        if (input && textOverride == null) input.value = "";

        appendMsg("user", text);
        history.push({ role: "user", content: text });

        var typing = appendMsg("bot", "Đang trả lời…", "beeseo-chatbot-msg--typing");
        setSending(true);

        var headers = { "Content-Type": "application/json" };
        var token = getToken();
        if (token) headers.Authorization = "Bearer " + token;

        try {
        var apiUrls = ["/api/chatbot/message", "/chatbot/message"];
        var res = null;
        var lastErr = null;
        for (var u = 0; u < apiUrls.length; u++) {
            try {
                res = await fetch(apiUrls[u], {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify({
                        message: text,
                        history: history.slice(0, -1),
                        page_path: pagePath(),
                        session_id: getSessionId(),
                    }),
                });
                if (res.status !== 404) break;
            } catch (e) {
                lastErr = e;
            }
        }
        if (!res) {
            throw lastErr || new Error("Không kết nối được máy chủ chatbot.");
        }
            var data = {};
            try {
                data = await res.json();
            } catch (_) {}
            if (!res.ok) {
                var detail = data.detail;
                if (Array.isArray(detail)) {
                    detail = detail.map(function (x) { return x.msg || x; }).join(", ");
                }
                if (res.status === 404) {
                    throw new Error(
                        "API chatbot chưa sẵn sàng (404). Hãy khởi động lại run.bat để nạp route mới."
                    );
                }
                throw new Error(detail || data.message || "HTTP " + res.status);
            }
            if (data.session_id) {
                sessionId = data.session_id;
                try {
                    sessionStorage.setItem(SESSION_KEY, sessionId);
                } catch (_) {}
            }
            var reply = String(data.reply || "").trim() || "Không nhận được phản hồi.";
            if (typing && typing.parentNode && typing.parentNode.parentNode) {
                typing.parentNode.parentNode.removeChild(typing.parentNode);
            }
            appendMsg("bot", reply);
            history.push({ role: "assistant", content: reply });
            if (history.length > 24) history = history.slice(-24);
        } catch (err) {
            if (typing && typing.parentNode && typing.parentNode.parentNode) {
                typing.parentNode.parentNode.removeChild(typing.parentNode);
            }
            appendMsg(
                "bot",
                "Lỗi: " +
                    (err && err.message ? err.message : String(err)) +
                    "\n\nChatbot dùng khóa API admin trong env.local. Nếu lỗi 404, khởi động lại run.bat."
            );
        } finally {
            setSending(false);
        }
    }

    function renderQuickPrompts(prompts) {
        var wrap = document.getElementById("beeseoChatbotQuick");
        if (!wrap) return;
        var list = prompts && prompts.length ? prompts : FALLBACK_PROMPTS;
        wrap.innerHTML = "";
        list.forEach(function (p) {
            var btn = document.createElement("button");
            btn.type = "button";
            btn.className = "beeseo-chatbot-quick-btn";
            if (p.id === "pricing") {
                btn.className += " beeseo-chatbot-quick-btn--pricing";
            }
            btn.textContent = p.label || p.id;
            btn.addEventListener("click", function () {
                sendMessage(p.label || "");
            });
            wrap.appendChild(btn);
        });
    }

    async function loadQuickPrompts() {
        try {
            var res = await fetch("/api/chatbot/prompts");
            if (res.status === 404) res = await fetch("/chatbot/prompts");
            if (!res.ok) throw new Error("prompts " + res.status);
            var data = await res.json();
            renderQuickPrompts(data.prompts || FALLBACK_PROMPTS);
        } catch (_) {
            renderQuickPrompts(FALLBACK_PROMPTS);
        }
    }

    function bind() {
        var root = document.getElementById(ROOT_ID);
        if (!root || root.dataset.bound) return;
        root.dataset.bound = "1";

        var fab = document.getElementById("beeseoChatbotFab");
        var closeBtn = document.getElementById("beeseoChatbotClose");
        var sendBtn = document.getElementById("beeseoChatbotSend");

        if (fab) fab.addEventListener("click", function () { setOpen(true); });
        if (closeBtn) closeBtn.addEventListener("click", function () { setOpen(false); });
        if (sendBtn) sendBtn.addEventListener("click", function () { sendMessage(); });

        var input = document.getElementById("beeseoChatbotInput");
        if (input) {
            input.addEventListener("keydown", function (e) {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
        }

        renderQuickPrompts(FALLBACK_PROMPTS);
        appendMsg(
            "bot",
            "Xin chào! Tôi là **trợ lý BeeSEO** — hỗ trợ Technical SEO, Content SEO và **bảng giá phần mềm**. " +
                "Bấm **Giá phần mềm bao nhiêu?** bên dưới hoặc nhập câu hỏi của bạn."
        );
        loadQuickPrompts();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bind);
    } else {
        bind();
    }
})();
