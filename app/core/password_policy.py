"""Shared password rules for register and first-time login (OTP activation)."""


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Mật khẩu cần ít nhất 8 ký tự.")
    if not any(c.isupper() for c in password):
        raise ValueError("Mật khẩu cần ít nhất 1 chữ hoa.")
    if not any(c.islower() for c in password):
        raise ValueError("Mật khẩu cần ít nhất 1 chữ thường.")
    if not any(c.isdigit() for c in password):
        raise ValueError("Mật khẩu cần ít nhất 1 chữ số.")
    return password
