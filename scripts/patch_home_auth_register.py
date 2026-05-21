#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "templates" / "home.html"
text = p.read_text(encoding="utf-8")

old_block = (
    '            <motion id="modalAuthMsg" class="modal-auth-msg"></div>\n'
    '            <button type="button" id="btnSubmitAuth" class="btn-submit">Đăng nhập</button>\n'
    '            <div style="height:10px;"></div>'
)
old_block = old_block.replace("<motion ", "<div ")

new_block = """            <button type="button" class="auth-switch-link" id="linkGoRegister">Chưa có tài khoản? Đăng ký</button>
            <button type="button" id="btnSubmitAuth" class="btn-submit">Đăng nhập</button>
            </div>

            <div id="authPanelRegister" class="auth-tab-panel" role="tabpanel" hidden>
                <p>Tạo tài khoản Gmail: nhận OTP → nhập OTP → đặt mật khẩu → bấm <strong>Đăng ký</strong>.</p>
                <input type="email" id="regEmail" placeholder="Email Gmail" autocomplete="email">
                <p class="modal-hint">Chỉ Gmail (@gmail.com) nhận được mã OTP.</p>
                <button type="button" id="btnRegOtpSend" class="btn-outline">Nhận mã OTP (gửi về Gmail)</button>
                <input type="text" id="regOtp" placeholder="Mã OTP trong email" inputmode="numeric" autocomplete="one-time-code">
                <label class="pw-label" for="regPassword">Tiêu chí mật khẩu</label>
                <ul id="regPwRules" class="pw-rules" aria-live="polite">
                    <li id="reg-rule-len">Ít nhất 8 ký tự</li>
                    <li id="reg-rule-up">Ít nhất 1 chữ hoa (A–Z)</li>
                    <li id="reg-rule-low">Ít nhất 1 chữ thường (a–z)</li>
                    <li id="reg-rule-num">Ít nhất 1 chữ số (0–9)</li>
                </ul>
                <div class="pw-wrap">
                    <input type="password" id="regPassword" placeholder="Mật khẩu mới" minlength="8" autocomplete="new-password">
                    <button type="button" class="pw-toggle" id="btnToggleRegPw" title="Hiện/ẩn mật khẩu" aria-label="Hiện mật khẩu">👁</button>
                </div>
                <button type="button" class="auth-switch-link" id="linkGoLogin">Đã có tài khoản? Đăng nhập</button>
                <button type="button" id="btnSubmitRegister" class="btn-submit">Đăng ký</button>
            </div>

            <div id="modalAuthMsg" class="modal-auth-msg"></div>
            <motion style="height:8px;"></motion>""".replace(
    "<motion ", "<div "
).replace("</motion>", "</div>")

if old_block not in text:
    raise SystemExit("old_block not found")
text = text.replace(old_block, new_block, 1)

js_marker = '    const authLoginHint = document.getElementById("authLoginHint");'
if "function setAuthTab" not in text and js_marker in text:
    js_insert = r'''
    const authPanelLogin = document.getElementById("authPanelLogin");
    const authPanelRegister = document.getElementById("authPanelRegister");
    const authTabLogin = document.getElementById("authTabLogin");
    const authTabRegister = document.getElementById("authTabRegister");
    const regEmail = document.getElementById("regEmail");
    const regOtp = document.getElementById("regOtp");
    const regPassword = document.getElementById("regPassword");
    const btnRegOtpSend = document.getElementById("btnRegOtpSend");
    const btnSubmitRegister = document.getElementById("btnSubmitRegister");
    const linkGoRegister = document.getElementById("linkGoRegister");
    const linkGoLogin = document.getElementById("linkGoLogin");
    const btnToggleRegPw = document.getElementById("btnToggleRegPw");

    function setAuthTab(tab) {
        const isLogin = tab === "login";
        if (authTabLogin) {
            authTabLogin.classList.toggle("active", isLogin);
            authTabLogin.setAttribute("aria-selected", isLogin ? "true" : "false");
        }
        if (authTabRegister) {
            authTabRegister.classList.toggle("active", !isLogin);
            authTabRegister.setAttribute("aria-selected", !isLogin ? "true" : "false");
        }
        if (authPanelLogin) authPanelLogin.hidden = !isLogin;
        if (authPanelRegister) authPanelRegister.hidden = isLogin;
        setModalAuthMsg("", "");
    }

    function fillLoginFromRegister(email, password) {
        if (authEmail) authEmail.value = email;
        if (authPassword) authPassword.value = password;
        if (authOtp) authOtp.value = "";
        updatePwRuleEls();
        syncAuthOtpUi();
    }

    function updateRegPwRuleEls() {
        if (!regPassword) return false;
        const v = regPassword.value;
        const len = v.length >= 8;
        const up = /[A-Z]/.test(v);
        const low = /[a-z]/.test(v);
        const num = /[0-9]/.test(v);
        const set = (id, ok) => { const el = document.getElementById(id); if (el) el.className = ok ? "ok" : ""; };
        set("reg-rule-len", len); set("reg-rule-up", up); set("reg-rule-low", low); set("reg-rule-num", num);
        return len && up && low && num;
    }

    if (regPassword) regPassword.addEventListener("input", updateRegPwRuleEls);
    if (btnToggleRegPw && regPassword) {
        btnToggleRegPw.addEventListener("click", function () {
            const isPw = regPassword.type === "password";
            regPassword.type = isPw ? "text" : "password";
            btnToggleRegPw.textContent = isPw ? "🙈" : "👁";
        });
    }

    document.querySelectorAll("[data-auth-tab]").forEach((btn) => {
        btn.addEventListener("click", () => setAuthTab(btn.getAttribute("data-auth-tab") || "login"));
    });
    if (linkGoRegister) linkGoRegister.addEventListener("click", () => setAuthTab("register"));
    if (linkGoLogin) linkGoLogin.addEventListener("click", () => setAuthTab("login"));

    async function sendRegOtp() {
        const email = (regEmail && regEmail.value || "").trim().toLowerCase();
        if (!email) { setModalAuthMsg("Nhập Gmail trước.", "error"); return; }
        if (!email.endsWith("@gmail.com") && !email.endsWith("@googlemail.com")) {
            setModalAuthMsg("Chỉ gửi OTP cho Gmail.", "error"); return;
        }
        try {
            setModalAuthMsg("Đang gửi mã OTP...", "");
            const r = await fetch("/auth/otp/send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email }),
            });
            const d = await r.json().catch(() => ({}));
            if (!r.ok) throw new Error(apiDetail(d));
            setModalAuthMsg(d.message || "Đã gửi OTP. Kiểm tra Gmail.", "ok");
        } catch (e) {
            setModalAuthMsg(String(e.message || e), "error");
        }
    }

    async function doRegister() {
        const email = (regEmail && regEmail.value || "").trim().toLowerCase();
        const password = regPassword ? regPassword.value : "";
        const otp = (regOtp && regOtp.value || "").trim().replace(/\s/g, "");
        if (!email || !password || !otp) {
            setModalAuthMsg("Nhập đủ Gmail, OTP và mật khẩu.", "error");
            return;
        }
        if (!email.endsWith("@gmail.com") && !email.endsWith("@googlemail.com")) {
            setModalAuthMsg("Chỉ đăng ký bằng Gmail (@gmail.com).", "error");
            return;
        }
        if (!updateRegPwRuleEls()) {
            setModalAuthMsg("Mật khẩu chưa đủ tiêu chí.", "error");
            return;
        }
        try {
            setModalAuthMsg("Đang đăng ký...", "");
            const r = await fetch("/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email, password: password, otp: otp }),
            });
            const d = await r.json().catch(() => ({}));
            if (!r.ok) throw new Error(apiDetail(d));
            fillLoginFromRegister(email, password);
            setAuthTab("login");
            setModalAuthMsg(
                (d.message || "Đăng ký thành công.") + " Đã điền sẵn email và mật khẩu — bấm Đăng nhập.",
                "ok"
            );
        } catch (e) {
            setModalAuthMsg(String(e.message || e), "error");
        }
    }

    if (btnRegOtpSend) btnRegOtpSend.addEventListener("click", sendRegOtp);
    if (btnSubmitRegister) btnSubmitRegister.addEventListener("click", doRegister);

'''
    text = text.replace(js_marker, js_insert + js_marker, 1)

old_pw = """        document.getElementById("rule-len").className = len ? "ok" : "";
        document.getElementById("rule-up").className = up ? "ok" : "";
        document.getElementById("rule-low").className = low ? "ok" : "";
        document.getElementById("rule-num").className = num ? "ok" : "";"""
new_pw = """        const setRule = (id, ok) => { const el = document.getElementById(id); if (el) el.className = ok ? "ok" : ""; };
        setRule("rule-len", len); setRule("rule-up", up); setRule("rule-low", low); setRule("rule-num", num);
        setRule("reg-rule-len", len); setRule("reg-rule-up", up); setRule("reg-rule-low", low); setRule("reg-rule-num", num);"""
if old_pw in text:
    text = text.replace(old_pw, new_pw, 1)

# declare authEmail before syncAuthOtpUi uses it
if "async function syncAuthOtpUi" in text and "const authEmail = document.getElementById" in text:
    chunk = text.split("async function syncAuthOtpUi")[0]
    if "const authEmail = document.getElementById" not in chunk.split("const authOtpBlock")[0]:
        text = text.replace(
            "    const authOtpBlock = document.getElementById(\"authOtpBlock\");\n    const authLoginHint",
            "    const authEmail = document.getElementById(\"authEmail\");\n    const authPassword = document.getElementById(\"authPassword\");\n    const authOtpBlock = document.getElementById(\"authOtpBlock\");\n    const authLoginHint",
        )
        text = text.replace(
            "\n    const authEmail = document.getElementById(\"authEmail\");\n    const authPassword = document.getElementById(\"authPassword\");\n    let token",
            "\n    let token",
            1,
        )

open_btn = '        authModal.hidden = false;\n        syncAuthOtpUi();'
open_btn_new = '        authModal.hidden = false;\n        setAuthTab("login");\n        syncAuthOtpUi();'
if open_btn in text and "setAuthTab(\"login\")" not in text.split(open_btn)[0][-200:]:
    text = text.replace(open_btn, open_btn_new, 1)

p.write_text(text, encoding="utf-8")
print("OK")
