"""Mat ma dung chung: bam mat khau, JWT, ma TOTP (2FA), token ngau nhien.

Khong dung toi DB - tra cuu nguoi dung / kiem quyen o app/modules/auth/deps.py.
"""
import base64
import hashlib
import io
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import pyotp
import qrcode
import qrcode.image.svg

from app.core.config import settings

JWT_ALGORITHM = "HS256"


def now() -> datetime:
    return datetime.now(timezone.utc)


# ---------- Mat khau ----------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode())
    except ValueError:
        return False


def password_problem(password: str) -> str | None:
    """Loi cua mat khau moi (tieng Viet de hien len form), hop le thi None."""
    if len(password) < 10:
        return "Mật khẩu tối thiểu 10 ký tự"
    if password.isdigit() or password.isalpha():
        return "Mật khẩu phải có cả chữ và số"
    return None


# ---------- JWT ----------
# type: "access" (goi API, 15 phut) | "mfa" (da qua mat khau, cho nhap ma 2FA, 5 phut)

def create_token(user_id: int, token_type: str, minutes: int, version: int = 0, **extra) -> str:
    payload = {"sub": str(user_id), "type": token_type, "ver": version,
               "iat": now(), "exp": now() + timedelta(minutes=minutes), **extra}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_token(token: str, token_type: str) -> dict | None:
    """Payload neu token hop le, dung loai va con han; khong thi None."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    return payload if payload.get("type") == token_type else None


# ---------- Token ngau nhien (refresh token, link dat lai mat khau) ----------

def random_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """DB chi luu hash - lo DB cung khong dung duoc token."""
    return hashlib.sha256(token.encode()).hexdigest()


# ---------- 2FA (TOTP) ----------

def new_totp_secret() -> str:
    return pyotp.random_base32()


def totp_uri(secret: str, email: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=settings.totp_issuer)


def verify_totp(secret: str, code: str) -> bool:
    code = "".join(ch for ch in str(code) if ch.isdigit())
    # valid_window=1: chap nhan lech dong ho +-30 giay
    return len(code) == 6 and pyotp.TOTP(secret).verify(code, valid_window=1)


def qr_svg_data_uri(text: str) -> str:
    """Ma QR dang SVG (data URI) de nhung thang vao <img>."""
    image = qrcode.make(text, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
    buffer = io.BytesIO()
    image.save(buffer)
    return "data:image/svg+xml;base64," + base64.b64encode(buffer.getvalue()).decode()


def new_backup_codes(count: int = 10) -> list[str]:
    """Ma du phong dang XXXX-XXXX, moi ma dung mot lan."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # bo O/0, I/1 cho de doc
    return ["-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(2)) for _ in range(count)]


def normalize_backup_code(code: str) -> str:
    raw = "".join(ch for ch in str(code).upper() if ch.isalnum())
    return f"{raw[:4]}-{raw[4:]}"
