"""Dang nhap / dang xuat / 2FA / mat khau - /api/v1/auth/...

Luong dang nhap:
    POST /login           -> step "done" (co cookie phien)
                           | "verify_2fa" (co cookie tam, nhap ma o POST /2fa/verify)
                           | "setup_2fa"  (vai tro bat buoc 2FA ma chua cai:
                                           POST /2fa/setup lay QR, POST /2fa/enable nhap ma)
    POST /refresh         -> cap lai access token khi het 15 phut (portal tu goi)
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    decode_token, hash_token, new_backup_codes, new_totp_secret, qr_svg_data_uri, totp_uri, verify_password,
)
from app.modules.auth import models, schemas, service
from app.modules.auth.deps import ACCESS_COOKIE, MFA_COOKIE, get_current_user, requires_2fa
from app.modules.system.service import record_event

router = APIRouter(prefix="/auth", tags=["auth"])


def _pending(request: Request, db: Session, token_type: str) -> tuple[models.User | None, bool]:
    """(nguoi dung, co "ghi nho thiet bi" khong) cua cookie tam - da qua mat khau, dang o buoc 2FA."""
    payload = decode_token(request.cookies.get(MFA_COOKIE, ""), token_type)
    if payload is None:
        return None, False
    user = db.get(models.User, int(payload["sub"]))
    if user is None or not user.is_active or user.deleted_at or payload.get("ver") != user.token_version:
        return None, False
    return user, bool(payload.get("remember"))


def _session_user(request: Request, db: Session) -> models.User | None:
    payload = decode_token(request.cookies.get(ACCESS_COOKIE, ""), "access")
    if payload is None:
        return None
    user = db.get(models.User, int(payload["sub"]))
    ok = user and user.is_active and not user.deleted_at and payload.get("ver") == user.token_version
    return user if ok else None


@router.post("/login", response_model=schemas.LoginOut)
def login(data: schemas.LoginIn, request: Request, response: Response, db: Session = Depends(get_db)):
    return service.login(db, data, request, response)


@router.post("/2fa/verify", response_model=schemas.LoginOut)
def verify_2fa(data: schemas.CodeIn, request: Request, response: Response, db: Session = Depends(get_db)):
    user, remember = _pending(request, db, "mfa")
    if user is None:
        raise HTTPException(401, "Hết thời gian nhập mã, vui lòng đăng nhập lại")
    return service.verify_second_factor(db, user, data.code, request, response, remember)


@router.post("/2fa/setup", response_model=schemas.TotpSetupOut)
def setup_2fa(request: Request, db: Session = Depends(get_db)):
    """Tao ma bi mat moi (chua bat) - luc dang nhap bat buoc, hoac tu trang Tai khoan."""
    user = _pending(request, db, "mfa_setup")[0] or _session_user(request, db)
    if user is None:
        raise HTTPException(401, "Hết thời gian, vui lòng đăng nhập lại")
    user.totp_secret_pending = new_totp_secret()
    db.commit()
    uri = totp_uri(user.totp_secret_pending, user.email)
    return schemas.TotpSetupOut(qr=qr_svg_data_uri(uri), secret=user.totp_secret_pending)


@router.post("/2fa/enable", response_model=schemas.BackupCodesOut)
def enable_2fa(data: schemas.CodeIn, request: Request, response: Response, db: Session = Depends(get_db)):
    pending, remember = _pending(request, db, "mfa_setup")
    user = pending or _session_user(request, db)
    if user is None:
        raise HTTPException(401, "Hết thời gian, vui lòng đăng nhập lại")
    codes = service.enable_totp(db, user, data.code, request)
    if pending:   # dang trong luong dang nhap -> vao luon
        record_event(db, "login.success", request, user=user, detail={"2fa": "setup"}, summary="Đăng nhập (cài 2FA)")
        session = service.start_session(db, user, request, response, remember)
        return schemas.BackupCodesOut(backup_codes=codes, user=session.user)
    return schemas.BackupCodesOut(backup_codes=codes)


@router.post("/2fa/disable", response_model=schemas.MeOut)
def disable_2fa(data: schemas.PasswordIn, request: Request, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    if requires_2fa(user):
        raise HTTPException(400, "Vai trò của bạn bắt buộc 2FA, không tắt được")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(400, "Mật khẩu không đúng")
    service.disable_totp(user)
    record_event(db, "2fa.disable", request, user=user, summary="Tắt xác thực 2 bước")
    db.commit()
    return service.me_out(user)


@router.post("/2fa/backup-codes", response_model=schemas.BackupCodesOut)
def regenerate_backup_codes(data: schemas.PasswordIn, request: Request, db: Session = Depends(get_db),
                            user: models.User = Depends(get_current_user)):
    """Tao bo 10 ma du phong moi - bo cu mat hieu luc."""
    if not user.totp_enabled:
        raise HTTPException(400, "Chưa bật 2FA")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(400, "Mật khẩu không đúng")
    codes = new_backup_codes()
    user.backup_codes = [hash_token(c) for c in codes]
    record_event(db, "2fa.backup_codes", request, user=user, summary="Tạo mã dự phòng 2FA mới")
    db.commit()
    return schemas.BackupCodesOut(backup_codes=codes)


@router.post("/refresh", response_model=schemas.MeOut)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    return service.refresh_session(db, request, response)


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    service.revoke_refresh(db, request)
    user = _session_user(request, db)
    if user:
        record_event(db, "logout", request, user=user, summary="Đăng xuất")
    db.commit()
    service.clear_cookies(response)
    return {"ok": True}


@router.get("/me", response_model=schemas.MeOut)
def me(user: models.User = Depends(get_current_user)):
    return service.me_out(user)


@router.post("/change-password", response_model=schemas.MeOut)
def change_password(data: schemas.ChangePasswordIn, request: Request, response: Response,
                    db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Doi mat khau: moi phien khac bi dang xuat, phien nay duoc cap lai."""
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(400, "Mật khẩu hiện tại không đúng")
    if data.new_password == data.current_password:
        raise HTTPException(400, "Mật khẩu mới phải khác mật khẩu hiện tại")
    service.set_password(user, data.new_password)
    user.must_change_password = False
    remember = service.current_session_remembered(db, request)   # giu kieu phien dang dung
    service.revoke_all_sessions(db, user)
    record_event(db, "password.change", request, user=user, summary="Đổi mật khẩu")
    return service.start_session(db, user, request, response, remember).user


@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotPasswordIn, request: Request, db: Session = Depends(get_db)):
    service.send_reset_link(db, data.email, request)
    return {"ok": True}   # giong nhau du email co ton tai hay khong


@router.post("/reset-password")
def reset_password(data: schemas.ResetPasswordIn, request: Request, db: Session = Depends(get_db)):
    service.reset_password(db, data, request)
    return {"ok": True}
