#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tool = ROOT / "templates" / "seo_tool.html"
text = tool.read_text(encoding="utf-8")
partial = (ROOT / "templates" / "partials" / "beeseo_auth_modal.html").read_text(encoding="utf-8")

start = text.find('    <div class="auth-modal" id="authModal" hidden>')
end = text.find('    <motion class="auth-modal account-mini-modal"', start)
if end < 0:
    end = text.find('    <div class="auth-modal account-mini-modal"', start)
if start < 0 or end < 0:
    raise SystemExit("auth modal block not found")

text = text[:start] + partial + "\n" + text[end:]

css = """
        .auth-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 14px;
        }
        .auth-tab {
            flex: 1;
            padding: 9px 12px;
            border-radius: 8px;
            border: 1px solid #dbe3ef;
            background: #f8fafc;
            color: #64748b;
            font-weight: 700;
            font-size: 0.88rem;
            cursor: pointer;
            font-family: inherit;
        }
        .auth-tab.active {
            background: #2563eb;
            border-color: #2563eb;
            color: #fff;
        }
        .auth-tab-panel[hidden] { display: none !important; }
        .auth-tab-panel > p { margin: 0 0 12px; text-align: center; color: #64748b; font-size: 0.9rem; }
        .auth-switch-link {
            display: block;
            width: 100%;
            margin: 4px 0 10px;
            padding: 0;
            border: 0;
            background: none;
            color: #2563eb;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            text-align: center;
            font-family: inherit;
            text-decoration: underline;
        }
        .modal-hint { font-size: 0.78rem; color: #94a3b8; margin: -8px 0 10px; text-align: center; }
"""
if ".auth-tabs" not in text:
    text = text.replace("        .auth-modal[hidden] { display: none; }", "        .auth-modal[hidden] { display: none; }\n" + css, 1)

# Inject register JS before doLogin in seo_tool
marker = "        async function doLogin() {"
home = (ROOT / "templates" / "home.html").read_text(encoding="utf-8")
h0 = home.find("    const authPanelLogin = document.getElementById")
h1 = home.find("    if (btnRegOtpSend) btnRegOtpSend.addEventListener", h0)
h2 = home.find("\n", h1) + 1
block = home[h0:h2]

if "function setAuthTab" not in text and marker in text:
    # seo_tool uses different element refs - patch block to use existing authEmail from tool script
    # insert after authOtp declaration
    ins = text.find('        const authOtp = document.getElementById("authOtp");')
    if ins > 0:
        ins_end = text.find("\n", ins) + 1
        # adapt block: use 8-space indent for tool script
        adapted = "\n".join("        " + ln if ln.strip() else ln for ln in block.splitlines())
        adapted = adapted.replace("    const ", "        const ")
        adapted = adapted.replace("    function ", "        function ")
        adapted = adapted.replace("    async function ", "        async function ")
        adapted = adapted.replace("    if (regPassword)", "        if (regPassword)")
        adapted = adapted.replace("    document.querySelectorAll", "        document.querySelectorAll")
        adapted = adapted.replace("    if (linkGoRegister)", "        if (linkGoRegister)")
        adapted = adapted.replace("    if (btnRegOtpSend)", "        if (btnRegOtpSend)")
        text = text[:ins_end] + adapted + text[ins_end:]

    # syncAuthOtpUi + open login tab
    if "async function syncAuthOtpUi" not in text:
        otp_block = home[home.find("    async function syncAuthOtpUi"): home.find("    let token = sessionStorage", home.find("async function syncAuthOtpUi"))]
        otp_block = "\n".join("        " + ln if ln.strip() else ln for ln in otp_block.splitlines())
        otp_block = otp_block.replace("    async function", "        async function").replace("    if (authEmail)", "        if (authEmail)")
        ins2 = text.find("        let token = sessionStorage.getItem")
        if ins2 > 0:
            text = text[:ins2] + otp_block + text[ins2:]

    open_old = "            authModal.hidden = false;\n        });"
    open_new = "            authModal.hidden = false;\n            if (typeof setAuthTab === \"function\") setAuthTab(\"login\");\n            if (typeof syncAuthOtpUi === \"function\") syncAuthOtpUi();\n        });"
    if open_old in text and "setAuthTab" not in text[text.find(open_old) - 100 : text.find(open_old)]:
        text = text.replace(open_old, open_new, 1)

    # updatePwRuleEls in seo_tool
    old_pw = '            document.getElementById("rule-len").className = len ? "ok" : "";'
    if old_pw in text and "reg-rule-len" not in text[text.find(old_pw) : text.find(old_pw) + 400]:
        text = text.replace(
            old_pw + '\n            document.getElementById("rule-up").className = up ? "ok" : "";\n            document.getElementById("rule-low").className = low ? "ok" : "";\n            document.getElementById("rule-num").className = num ? "ok" : "";',
            '            const setRule = (id, ok) => { const el = document.getElementById(id); if (el) el.className = ok ? "ok" : ""; };\n            setRule("rule-len", len); setRule("rule-up", up); setRule("rule-low", low); setRule("rule-num", num);\n            setRule("reg-rule-len", len); setRule("reg-rule-up", up); setRule("reg-rule-low", low); setRule("reg-rule-num", num);',
            1,
        )

tool.write_text(text, encoding="utf-8")
print("patched seo_tool.html")
