"""Dependency cho FastAPI: nguoi dang dang nhap va kiem quyen.

Dung o module khac:
    router.include_router(customers.router, dependencies=[Depends(guard("common.customers"))])
      -> GET can `common.customers.view`, POST `.create`, PUT/PATCH `.update`, DELETE `.delete`
    @router.get(..., dependencies=[Depends(require("system.audit_log.view"))])
"""
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.modules.auth import models
from app.modules.auth.permissions import ALL

ACCESS_COOKIE = "dl_access"
REFRESH_COOKIE = "dl_refresh"
MFA_COOKIE = "dl_mfa"

METHOD_ACTIONS = {"GET": "view", "HEAD": "view", "OPTIONS": "view",
                  "POST": "create", "PUT": "update", "PATCH": "update", "DELETE": "delete"}


def user_permissions(user: models.User) -> set[str]:
    return {permission.code for role in user.roles for permission in role.permissions}


def has_permission(user: models.User, code: str) -> bool:
    codes = user_permissions(user)
    return ALL in codes or code in codes


def requires_2fa(user: models.User) -> bool:
    return settings.two_factor_enabled and any(role.require_2fa for role in user.roles)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    """Nguoi dung cua cookie access. Het han / sai -> 401 (portal tu goi /auth/refresh roi thu lai)."""
    payload = decode_token(request.cookies.get(ACCESS_COOKIE, ""), "access")
    if payload is None:
        raise HTTPException(401, "Phiên đăng nhập đã hết hạn")
    user = db.get(models.User, int(payload["sub"]))
    # token_version tang khi doi/dat lai mat khau -> moi token cu het hieu luc ngay
    if (user is None or not user.is_active or user.deleted_at is not None
            or payload.get("ver") != user.token_version):
        raise HTTPException(401, "Phiên đăng nhập đã hết hạn")
    # Cho nhat ky thao tac (system.service.AuditMiddleware). Luu gia tri thuong: doi tuong
    # user het han sau khi endpoint commit va dong session.
    request.state.audit_user = (user.id, user.email)
    return user


def _check(user: models.User, code: str) -> None:
    if user.must_change_password:
        raise HTTPException(403, "Bạn cần đổi mật khẩu tạm trước khi tiếp tục")
    if not has_permission(user, code):
        raise HTTPException(403, f"Bạn không có quyền thực hiện thao tác này ({code})")


def require(code: str):
    """Can dung quyen `code`."""
    def dependency(user: models.User = Depends(get_current_user)) -> models.User:
        _check(user, code)
        return user
    return dependency


def guard(resource: str, overrides: dict[str, str] | None = None):
    """Quyen theo phuong thuc HTTP (METHOD_ACTIONS). overrides: duong dan ket thuc bang
    ... -> hanh dong, cho route khong dung kieu (vd POST "/preview-sheet" chi la xem)."""
    def dependency(request: Request, user: models.User = Depends(get_current_user)) -> models.User:
        path = request.url.path
        action = next((a for suffix, a in (overrides or {}).items() if path.endswith(suffix)),
                      METHOD_ACTIONS.get(request.method, "update"))
        _check(user, f"{resource}.{action}")
        return user
    return dependency
