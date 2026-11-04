"""Nghiep vu dang nhap: mat khau -> (2FA) -> phien; khoa tam; quen / doi mat khau."""
from datetime import timedelta

from fastapi import HTTPException, Request, Response
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.mailer import send_email
from app.core.security import (
    create_token, hash_password, hash_token, new_backup_codes, normalize_backup_code,
    now, password_problem, random_token, verify_password, verify_totp,
)
from app.modules.auth import models, schemas
from app.modules.auth.deps import (
    ACCESS_COOKIE, MFA_COOKIE, REFRESH_COOKIE, requires_2fa, user_permissions,
)
from app.modules.system.service import client_ip, record_event

MFA_MINUTES = 5
API_COOKIE_PATH = "/api"
AUTH_COOKIE_PATH = "/api/v1/auth"


# ---------- Cookie ----------

def _set_cookie(response: Response, name: str, value: str, max_age: int | None, path: str) -> None:
    """max_age None = cookie phien: trinh duyet xoa khi tat."""
    response.set_cookie(
        name, value, max_age=max_age, path=path,
        httponly=True, secure=settings.cookie_secure, samesite="lax",
    )


def active_users(db: Session):
    """Tai khoan chua bi xoa mem."""
    return db.query(models.User).filter(models.User.deleted_at.is_(None))


def find_login_user(db: Session, identifier: str) -> models.User | None:
    """Tim theo email hoac ma nhan vien (khong phan biet hoa thuong)."""
    return active_users(db).filter(or_(
        models.User.email == identifier, func.lower(models.User.employee_code) == identifier,
    )).first()


def clear_cookies(response: Response) -> None:
    for name, path in ((ACCESS_COOKIE, API_COOKIE_PATH), (REFRESH_COOKIE, AUTH_COOKIE_PATH),
                       (MFA_COOKIE, AUTH_COOKIE_PATH)):
        response.delete_cookie(name, path=path)


def me_out(user: models.User) -> schemas.MeOut:
    return schemas.MeOut(
        id=user.id, email=user.email, employee_code=user.employee_code, department=user.department,
        full_name=user.full_name,
        roles=[schemas.RoleBrief(code=r.code, name=r.name) for r in user.roles],
        permissions=sorted(user_permissions(user)),
        totp_enabled=user.totp_enabled, require_2fa=requires_2fa(user),
        must_change_password=user.must_change_password,
    )


def start_session(db: Session, user: models.User, request: Request, response: Response,
                  remember: bool = False) -> schemas.LoginOut:
    """Cap cookie access (15 phut) + refresh. Ghi nho thiet bi: refresh 30 ngay; khong ghi
    nho: cookie phien (mat khi tat trinh duyet), phia may chu toi da 12 gio. Commit."""
    refresh = random_token()
    lifetime = timedelta(days=settings.remember_days) if remember else timedelta(hours=settings.session_hours)
    db.add(models.RefreshToken(
        user_id=user.id, token_hash=hash_token(refresh), expires_at=now() + lifetime, remember=remember,
        user_agent=(request.headers.get("user-agent") or "")[:255], ip=client_ip(request),
    ))
    user.last_login_at = now()
    db.commit()
    access = create_token(user.id, "access", settings.access_token_minutes, user.token_version)
    _set_cookie(response, ACCESS_COOKIE, access,
                settings.access_token_minutes * 60 if remember else None, API_COOKIE_PATH)
    _set_cookie(response, REFRESH_COOKIE, refresh,
                int(lifetime.total_seconds()) if remember else None, AUTH_COOKIE_PATH)
    response.delete_cookie(MFA_COOKIE, path=AUTH_COOKIE_PATH)
    return schemas.LoginOut(step="done", user=me_out(user))


def _mfa_step(user: models.User, response: Response, step: str, remember: bool) -> schemas.LoginOut:
    """Da qua mat khau, cho buoc 2FA: cookie tam 5 phut, chua goi duoc API nao khac. Lua chon
    "ghi nho thiet bi" nam trong token de xong 2FA mo dung loai phien."""
    token_type = "mfa" if step == "verify_2fa" else "mfa_setup"
    token = create_token(user.id, token_type, MFA_MINUTES, user.token_version, remember=remember)
    _set_cookie(response, MFA_COOKIE, token, MFA_MINUTES * 60, AUTH_COOKIE_PATH)
    return schemas.LoginOut(step=step)


# ---------- Dang nhap ----------

def login(db: Session, data: schemas.LoginIn, request: Request, response: Response) -> schemas.LoginOut:
    user = find_login_user(db, data.identifier)
    # Cung mot thong bao cho "khong co tai khoan" va "sai mat khau" - khong lo tai khoan nao ton tai
    wrong = HTTPException(401, "Tài khoản hoặc mật khẩu không đúng")

    if user is None:
        record_event(db, "login.fail", request, email=data.identifier[:150], status=401,
                     detail={"reason": "no_user"}, summary=f"Đăng nhập sai: {data.identifier[:60]}")
        db.commit()
        raise wrong
    if user.locked_until and user.locked_until > now():
        minutes = int((user.locked_until - now()).total_seconds() // 60) + 1
        raise HTTPException(423, f"Tài khoản tạm khoá do sai mật khẩu nhiều lần. Thử lại sau {minutes} phút.")
    if not verify_password(data.password, user.password_hash):
        user.failed_logins += 1
        detail = {"reason": "wrong_password", "attempt": user.failed_logins}
        if user.failed_logins >= settings.login_max_attempts:
            user.locked_until = now() + timedelta(minutes=settings.login_lock_minutes)
            user.failed_logins = 0
            detail["locked"] = True
        record_event(db, "login.fail", request, user=user, status=401, detail=detail,
                     summary="Đăng nhập sai mật khẩu" + (" — tạm khoá" if detail.get("locked") else ""))
        db.commit()
        raise wrong
    if not user.is_active:
        raise HTTPException(403, "Tài khoản đã bị khoá. Liên hệ quản trị viên.")

    user.failed_logins = 0
    user.locked_until = None
    db.commit()
    if settings.two_factor_enabled and user.totp_enabled:
        return _mfa_step(user, response, "verify_2fa", data.remember)
    if requires_2fa(user):
        return _mfa_step(user, response, "setup_2fa", data.remember)
    record_event(db, "login.success", request, user=user, summary="Đăng nhập")
    return start_session(db, user, request, response, data.remember)


def check_second_factor(user: models.User, code: str) -> bool:
    """Ma TOTP, hoac mot ma du phong (dung xong thi xoa)."""
    if user.totp_secret and verify_totp(user.totp_secret, code):
        return True
    hashed = hash_token(normalize_backup_code(code))
    if hashed in (user.backup_codes or []):
        user.backup_codes = [c for c in user.backup_codes if c != hashed]
        return True
    return False


def verify_second_factor(db: Session, user: models.User, code: str, request: Request,
                         response: Response, remember: bool) -> schemas.LoginOut:
    if not check_second_factor(user, code):
        record_event(db, "login.2fa_fail", request, user=user, status=401, summary="Nhập sai mã 2FA")
        db.commit()
        raise HTTPException(401, "Mã xác thực không đúng")
    record_event(db, "login.success", request, user=user, detail={"2fa": True}, summary="Đăng nhập (2FA)")
    return start_session(db, user, request, response, remember)


# ---------- 2FA ----------

def enable_totp(db: Session, user: models.User, code: str, request: Request) -> list[str]:
    if not user.totp_secret_pending or not verify_totp(user.totp_secret_pending, code):
        raise HTTPException(400, "Mã không đúng. Kiểm tra giờ trên điện thoại rồi thử lại.")
    user.totp_secret = user.totp_secret_pending
    user.totp_secret_pending = None
    user.totp_enabled = True
    codes = new_backup_codes()
    user.backup_codes = [hash_token(c) for c in codes]
    record_event(db, "2fa.enable", request, user=user, summary="Bật xác thực 2 bước")
    db.commit()
    return codes


def disable_totp(user: models.User) -> None:
    user.totp_secret = None
    user.totp_secret_pending = None
    user.totp_enabled = False
    user.backup_codes = []


# ---------- Phien ----------

def refresh_session(db: Session, request: Request, response: Response) -> schemas.MeOut:
    token = request.cookies.get(REFRESH_COOKIE, "")
    row = None
    if token:
        row = db.query(models.RefreshToken).filter(models.RefreshToken.token_hash == hash_token(token)).first()
    expired = HTTPException(401, "Phiên đăng nhập đã hết hạn")
    if row is None:
        raise expired
    if row.revoked_at is not None:
        # Token da dung roi lai duoc gui lai: co the bi lay cap -> thu hoi moi phien cua user
        db.query(models.RefreshToken).filter(
            models.RefreshToken.user_id == row.user_id, models.RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": now()})
        record_event(db, "session.reuse_detected", request, user=db.get(models.User, row.user_id), status=401,
                     summary="Phiên cũ bị dùng lại — đã đăng xuất mọi thiết bị")
        db.commit()
        raise expired
    user = db.get(models.User, row.user_id)
    if row.expires_at <= now() or user is None or not user.is_active or user.deleted_at:
        raise expired
    row.revoked_at = now()   # xoay vong: moi refresh token chi dung mot lan
    return start_session(db, user, request, response, row.remember).user


def current_session_remembered(db: Session, request: Request) -> bool:
    """Phien dang dung co "ghi nho thiet bi" khong (theo refresh token trong cookie)."""
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        return False
    row = db.query(models.RefreshToken).filter(models.RefreshToken.token_hash == hash_token(token)).first()
    return bool(row and row.remember)


def revoke_refresh(db: Session, request: Request) -> None:
    token = request.cookies.get(REFRESH_COOKIE)
    if token:
        db.query(models.RefreshToken).filter(
            models.RefreshToken.token_hash == hash_token(token), models.RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": now()})


def revoke_all_sessions(db: Session, user: models.User) -> None:
    """Doi/dat lai mat khau, khoa tai khoan: access token cu het hieu luc (token_version) + thu hoi refresh."""
    user.token_version += 1
    db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user.id, models.RefreshToken.revoked_at.is_(None),
    ).update({"revoked_at": now()})


# ---------- Mat khau ----------

def set_password(user: models.User, password: str) -> None:
    problem = password_problem(password)
    if problem:
        raise HTTPException(400, problem)
    user.password_hash = hash_password(password)


def send_reset_link(db: Session, email: str, request: Request) -> None:
    """Luon tra ve binh thuong - khong cho biet email co ton tai hay khong."""
    user = active_users(db).filter(models.User.email == email, models.User.is_active.is_(True)).first()
    if user is None:
        return
    recent = db.query(models.PasswordReset).filter(
        models.PasswordReset.user_id == user.id,
        models.PasswordReset.created_at > now() - timedelta(minutes=1),
    ).first()
    if recent:   # chong bam lien tuc
        return
    token = random_token()
    db.add(models.PasswordReset(
        user_id=user.id, token_hash=hash_token(token),
        expires_at=now() + timedelta(minutes=settings.password_reset_minutes),
    ))
    record_event(db, "password.reset_requested", request, user=user, summary="Yêu cầu đặt lại mật khẩu")
    db.commit()

    link = f"{settings.portal_url.rstrip('/')}/reset-password?token={token}"
    minutes = settings.password_reset_minutes
    send_email(
        user.email, "Đặt lại mật khẩu — Daliang VN",
        html=(f"<p>Chào {user.full_name},</p><p>Bấm vào link dưới đây để đặt mật khẩu mới "
              f"(hết hạn sau {minutes} phút, chỉ dùng được một lần):</p>"
              f'<p><a href="{link}">{link}</a></p>'
              "<p>Nếu bạn không yêu cầu, hãy bỏ qua email này.</p>"),
        text=f"Đặt lại mật khẩu (hết hạn sau {minutes} phút): {link}",
    )


def reset_password(db: Session, data: schemas.ResetPasswordIn, request: Request) -> None:
    row = db.query(models.PasswordReset).filter(models.PasswordReset.token_hash == hash_token(data.token)).first()
    if row is None or row.used_at is not None or row.expires_at <= now():
        raise HTTPException(400, "Link đặt lại mật khẩu không đúng hoặc đã hết hạn. Hãy yêu cầu link mới.")
    user = db.get(models.User, row.user_id)
    set_password(user, data.new_password)
    user.must_change_password = False
    user.failed_logins = 0
    user.locked_until = None
    row.used_at = now()
    revoke_all_sessions(db, user)
    record_event(db, "password.reset", request, user=user, summary="Đặt lại mật khẩu qua email")
    db.commit()
