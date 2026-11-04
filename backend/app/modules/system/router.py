"""Quan tri he thong - /api/v1/system/{users, roles, permissions, departments, audit-logs}.

Bang tai khoan/vai tro thuoc module auth; module nay chi co trang quan ly va
nhat ky thao tac. Moi thao tac tren tai khoan ghi nhat ky bang cau cu the
(mark_request) - vd "Khoá tài khoản Nguyễn Văn An".
"""
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, now
from app.modules.auth import models as auth_models
from app.modules.auth.deps import require, requires_2fa
from app.modules.auth.models import DEPARTMENTS
from app.modules.auth.permissions import ALL
from app.modules.auth.service import active_users, disable_totp, revoke_all_sessions
from app.modules.system import models, schemas
from app.modules.system.service import mark_request

router = APIRouter(prefix="/system")
users = APIRouter(prefix="/users", tags=["system-users"], dependencies=[Depends(require("system.users.manage"))])
roles = APIRouter(tags=["system-roles"], dependencies=[Depends(require("system.roles.manage"))])
logs = APIRouter(prefix="/audit-logs", tags=["system-audit-log"], dependencies=[Depends(require("system.audit_log.view"))])

User = auth_models.User
Role = auth_models.Role


# ---------- Tai khoan ----------

def _user_out(user: User) -> schemas.UserOut:
    return schemas.UserOut(
        id=user.id, email=user.email, employee_code=user.employee_code, department=user.department,
        full_name=user.full_name, is_active=user.is_active,
        totp_enabled=user.totp_enabled, require_2fa=requires_2fa(user),
        must_change_password=user.must_change_password,
        locked_until=user.locked_until, last_login_at=user.last_login_at, created_at=user.created_at,
        roles=[{"code": r.code, "name": r.name} for r in user.roles], role_ids=[r.id for r in user.roles],
    )


def _get_user(db: Session, user_id: int) -> User:
    user = active_users(db).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(404, "Không tìm thấy tài khoản")
    return user


def _roles(db: Session, role_ids: list[int]) -> list[Role]:
    found = db.query(Role).filter(Role.id.in_(role_ids)).all() if role_ids else []
    if len(found) != len(set(role_ids)):
        raise HTTPException(400, "Có vai trò không tồn tại")
    return found


def _full_admins(db: Session) -> list[User]:
    """Tai khoan dang hoat dong co quyen "*" - phai con it nhat mot."""
    return [
        u for u in active_users(db).filter(User.is_active.is_(True))
        if any(p.code == ALL for r in u.roles for p in r.permissions)
    ]


def _keep_an_admin(db: Session, had_admin: bool) -> None:
    db.flush()
    if had_admin and not _full_admins(db):
        db.rollback()
        raise HTTPException(400, "Phải còn ít nhất một tài khoản Admin cao nhất đang hoạt động")


def _unique(db: Session, email: str | None, employee_code: str | None, exclude_id: int | None = None) -> None:
    others = active_users(db).filter(User.id != exclude_id) if exclude_id else active_users(db)
    if email and others.filter(User.email == email).first():
        raise HTTPException(400, "Email này đã có tài khoản")
    if employee_code and others.filter(func.upper(User.employee_code) == employee_code).first():
        raise HTTPException(400, "Mã nhân viên này đã có tài khoản")


def _temporary_password() -> str:
    return secrets.token_urlsafe(9) + "7"   # luon co chu so: qua duoc kiem tra do manh


@users.get("", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return [_user_out(u) for u in active_users(db).order_by(User.full_name)]


@users.get("/summary", response_model=schemas.UsersSummaryOut)
def users_summary(db: Session = Depends(get_db)):
    active = active_users(db).filter(User.is_active.is_(True))
    failed = db.query(func.count(models.AuditLog.id)).filter(
        models.AuditLog.action.like("login.%fail"),
        models.AuditLog.created_at > now() - timedelta(hours=24),
    ).scalar()
    return schemas.UsersSummaryOut(
        active_users=active.count(),
        roles=db.query(func.count(Role.id)).scalar(),
        without_2fa=active.filter(User.totp_enabled.is_(False)).count(),
        failed_logins_24h=failed,
    )


@users.post("", response_model=schemas.TemporaryPasswordOut, status_code=201)
def create_user(data: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    _unique(db, data.email, data.employee_code)
    password = _temporary_password()
    user = User(email=data.email, employee_code=data.employee_code, department=data.department,
                full_name=data.full_name.strip(), password_hash=hash_password(password),
                must_change_password=True, roles=_roles(db, data.role_ids))
    db.add(user)
    db.commit()
    mark_request(request, f"Thêm tài khoản {user.full_name}", "user.create")
    return schemas.TemporaryPasswordOut(user=_user_out(user), temporary_password=password)


@users.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, data: schemas.UserUpdate, request: Request, db: Session = Depends(get_db)):
    user = _get_user(db, user_id)
    _unique(db, None, data.employee_code, exclude_id=user.id)
    had_admin = bool(_full_admins(db))
    user.full_name = data.full_name.strip()
    user.employee_code = data.employee_code
    user.department = data.department
    user.roles = _roles(db, data.role_ids)
    if not data.is_active and user.is_active:
        revoke_all_sessions(db, user)   # khoa -> dang xuat ngay moi noi
    user.is_active = data.is_active
    _keep_an_admin(db, had_admin)
    db.commit()
    mark_request(request, f"Sửa tài khoản {user.full_name}", "user.update")
    return _user_out(user)


@users.patch("/{user_id}/active", response_model=schemas.UserOut)
def set_user_active(user_id: int, data: schemas.ActiveIn, request: Request, db: Session = Depends(get_db)):
    """Nut o khoa tren bang: khoa / mo tai khoan."""
    user = _get_user(db, user_id)
    had_admin = bool(_full_admins(db))
    if not data.is_active and user.is_active:
        revoke_all_sessions(db, user)
    user.is_active = data.is_active
    _keep_an_admin(db, had_admin)
    db.commit()
    verb = "Mở khoá" if data.is_active else "Khoá"
    mark_request(request, f"{verb} tài khoản {user.full_name}", "user.unlock" if data.is_active else "user.lock")
    return _user_out(user)


@users.delete("/{user_id}")
def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    """Xoa mem: an khoi danh sach, khong dang nhap duoc; nhat ky va chung tu van biet ai
    lam. Email / ma nhan vien duoc giai phong de dung cho tai khoan khac."""
    user = _get_user(db, user_id)
    had_admin = bool(_full_admins(db))
    user.deleted_at = now()
    user.is_active = False
    revoke_all_sessions(db, user)
    _keep_an_admin(db, had_admin)
    db.commit()
    mark_request(request, f"Xoá tài khoản {user.full_name}", "user.delete")
    return {"ok": True}


@users.post("/{user_id}/reset-password", response_model=schemas.TemporaryPasswordOut)
def reset_user_password(user_id: int, request: Request, db: Session = Depends(get_db)):
    """Cap mat khau tam (nhan vien quen mat khau ma khong nhan duoc email)."""
    user = _get_user(db, user_id)
    password = _temporary_password()
    user.password_hash = hash_password(password)
    user.must_change_password = True
    user.failed_logins = 0
    user.locked_until = None
    revoke_all_sessions(db, user)
    db.commit()
    mark_request(request, f"Cấp mật khẩu tạm cho {user.full_name}", "user.reset_password")
    return schemas.TemporaryPasswordOut(user=_user_out(user), temporary_password=password)


@users.post("/{user_id}/reset-2fa", response_model=schemas.UserOut)
def reset_user_2fa(user_id: int, request: Request, db: Session = Depends(get_db)):
    """Go 2FA (nhan vien mat dien thoai va het ma du phong). Vai tro bat buoc 2FA thi lan
    dang nhap sau phai cai lai."""
    user = _get_user(db, user_id)
    disable_totp(user)
    revoke_all_sessions(db, user)
    db.commit()
    mark_request(request, f"Gỡ 2FA của {user.full_name}", "user.reset_2fa")
    return _user_out(user)


@users.post("/{user_id}/unlock", response_model=schemas.UserOut)
def unlock_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    """Mo khoa tam (do sai mat khau nhieu lan)."""
    user = _get_user(db, user_id)
    user.failed_logins = 0
    user.locked_until = None
    db.commit()
    mark_request(request, f"Mở khoá tạm cho {user.full_name}", "user.unlock")
    return _user_out(user)


@router.get("/departments", response_model=list[schemas.DepartmentOut],
            dependencies=[Depends(require("system.users.manage"))])
def list_departments():
    return [schemas.DepartmentOut(code=code, name=name) for code, name in DEPARTMENTS.items()]


# ---------- Vai tro ----------

def _role_out(db: Session, role: Role) -> schemas.RoleOut:
    count = (
        db.query(func.count()).select_from(auth_models.user_roles)
        .join(User, User.id == auth_models.user_roles.c.user_id)
        .filter(auth_models.user_roles.c.role_id == role.id, User.deleted_at.is_(None))
        .scalar()
    )
    return schemas.RoleOut(
        id=role.id, code=role.code, name=role.name, description=role.description,
        require_2fa=role.require_2fa, is_system=role.is_system,
        permission_codes=sorted(p.code for p in role.permissions), user_count=count,
    )


def _permissions(db: Session, codes: list[str]) -> list[auth_models.Permission]:
    found = db.query(auth_models.Permission).filter(auth_models.Permission.code.in_(codes)).all() if codes else []
    if len(found) != len(set(codes)):
        raise HTTPException(400, "Có quyền không tồn tại")
    return found


@roles.get("/permissions", response_model=list[schemas.PermissionOut])
def list_permissions(db: Session = Depends(get_db)):
    return db.query(auth_models.Permission).order_by(auth_models.Permission.module, auth_models.Permission.code).all()


@roles.get("/roles", response_model=list[schemas.RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return [_role_out(db, r) for r in db.query(Role).order_by(Role.id)]


@roles.post("/roles", response_model=schemas.RoleOut, status_code=201)
def create_role(data: schemas.RoleIn, request: Request, db: Session = Depends(get_db)):
    if db.query(Role).filter(Role.code == data.code).first():
        raise HTTPException(400, "Mã vai trò đã có")
    role = Role(code=data.code, name=data.name, description=data.description,
                require_2fa=data.require_2fa, permissions=_permissions(db, data.permission_codes))
    db.add(role)
    db.commit()
    mark_request(request, f"Thêm vai trò {role.name}", "role.create")
    return _role_out(db, role)


@roles.put("/roles/{role_id}", response_model=schemas.RoleOut)
def update_role(role_id: int, data: schemas.RoleIn, request: Request, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(404, "Không tìm thấy vai trò")
    had_admin = bool(_full_admins(db))
    if not role.is_system:
        role.code = data.code   # ma cua vai tro co san dung trong code, khong cho doi
    role.name = data.name
    role.description = data.description
    role.require_2fa = data.require_2fa
    role.permissions = _permissions(db, data.permission_codes)
    _keep_an_admin(db, had_admin)
    db.commit()
    mark_request(request, f"Sửa quyền vai trò {role.name}", "role.update")
    return _role_out(db, role)


@roles.delete("/roles/{role_id}")
def delete_role(role_id: int, request: Request, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(404, "Không tìm thấy vai trò")
    if role.is_system:
        raise HTTPException(400, "Vai trò có sẵn của hệ thống, không xoá được")
    if _role_out(db, role).user_count:
        raise HTTPException(400, "Vai trò đang được gán cho tài khoản, gỡ ra trước khi xoá")
    name = role.name
    db.delete(role)
    db.commit()
    mark_request(request, f"Xoá vai trò {name}", "role.delete")
    return {"ok": True}


# ---------- Nhat ky ----------

@logs.get("", response_model=schemas.AuditLogPage)
def list_audit_logs(
    user_id: int | None = None,
    module: str | None = None,
    action: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(models.AuditLog, User.full_name).outerjoin(User, User.id == models.AuditLog.user_id)
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    if module:
        query = query.filter(models.AuditLog.module == module)
    if action:
        query = query.filter(models.AuditLog.action.ilike(f"{action}%"))
    total = query.count()
    rows = (query.order_by(models.AuditLog.id.desc())
            .offset((page - 1) * page_size).limit(page_size).all())
    items = [
        schemas.AuditLogOut(
            id=log.id, created_at=log.created_at, user_id=log.user_id, user_email=log.user_email,
            user_name=name, action=log.action, module=log.module, summary=log.summary, path=log.path,
            status=log.status, ip=log.ip, detail=log.detail,
        )
        for log, name in rows
    ]
    return schemas.AuditLogPage(items=items, total=total, page=page, page_size=page_size)


for part in (users, roles, logs):
    router.include_router(part)
