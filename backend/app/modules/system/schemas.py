"""Du lieu vao/ra cua trang quan tri he thong."""
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.schemas import ORM_CONFIG
from app.modules.auth.models import DEPARTMENTS
from app.modules.auth.schemas import RoleBrief, clean_email


def _clean_code(value: Optional[str]) -> Optional[str]:
    value = (value or "").strip().upper()
    return value or None


def _check_department(value: Optional[str]) -> Optional[str]:
    if value and value not in DEPARTMENTS:
        raise ValueError("Bộ phận không hợp lệ")
    return value or None


# ---------- Tai khoan ----------

class UserOut(BaseModel):
    id: int
    email: str
    employee_code: Optional[str] = None
    department: Optional[str] = None
    full_name: str
    is_active: bool
    totp_enabled: bool
    require_2fa: bool
    must_change_password: bool
    locked_until: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    roles: List[RoleBrief] = []
    role_ids: List[int] = []


class UserCreate(BaseModel):
    email: str
    employee_code: Optional[str] = Field(default=None, max_length=20)
    department: Optional[str] = None
    full_name: str = Field(min_length=1, max_length=150)
    role_ids: List[int] = []

    _email = field_validator("email")(clean_email)
    _code = field_validator("employee_code")(_clean_code)
    _department = field_validator("department")(_check_department)


class UserUpdate(BaseModel):
    employee_code: Optional[str] = Field(default=None, max_length=20)
    department: Optional[str] = None
    full_name: str = Field(min_length=1, max_length=150)
    role_ids: List[int] = []
    is_active: bool = True

    _code = field_validator("employee_code")(_clean_code)
    _department = field_validator("department")(_check_department)


class ActiveIn(BaseModel):
    is_active: bool


class TemporaryPasswordOut(BaseModel):
    """Mat khau tam chi hien MOT lan - admin chuyen cho nhan vien, doi o lan dang nhap dau."""
    user: UserOut
    temporary_password: str


class UsersSummaryOut(BaseModel):
    """Bon the so lieu dau trang Nguoi dung & phan quyen."""
    active_users: int
    roles: int
    without_2fa: int          # tai khoan dang hoat dong chua bat 2FA
    failed_logins_24h: int


class DepartmentOut(BaseModel):
    code: str
    name: str


# ---------- Vai tro ----------

class PermissionOut(BaseModel):
    code: str
    module: str
    description: str
    model_config = ORM_CONFIG


class RoleOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    require_2fa: bool
    is_system: bool
    permission_codes: List[str]
    user_count: int


class RoleIn(BaseModel):
    code: str = Field(min_length=2, max_length=50, pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    require_2fa: bool = False
    permission_codes: List[str] = []


# ---------- Nhat ky ----------

class AuditLogOut(BaseModel):
    id: int
    created_at: datetime
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None       # ten hien tai cua tai khoan (neu con)
    action: str
    module: Optional[str] = None
    summary: Optional[str] = None
    path: Optional[str] = None
    status: Optional[int] = None
    ip: Optional[str] = None
    detail: Optional[Any] = None


class AuditLogPage(BaseModel):
    items: List[AuditLogOut]
    total: int
    page: int
    page_size: int
