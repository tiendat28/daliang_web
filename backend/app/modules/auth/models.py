"""Tai khoan, vai tro, quyen va phien dang nhap (schema `auth`).

Quyen dat ten `module.doi_tuong.hanh_dong` (vd `lab.test_processes.update`); danh
sach quyen khai trong code (app/modules/auth/permissions.py) va dong bo vao
bang `permissions` luc khoi dong. Vai tro giu quyen "*" la co moi quyen.
"""
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Table, Text, func, text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

SCHEMA = "auth"


class _InSchema:
    __table_args__ = {"schema": SCHEMA}


user_roles = Table(
    "user_roles", Base.metadata,
    Column("user_id", Integer, ForeignKey("auth.users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("auth.roles.id", ondelete="CASCADE"), primary_key=True),
    schema=SCHEMA,
)

role_permissions = Table(
    "role_permissions", Base.metadata,
    Column("role_id", Integer, ForeignKey("auth.roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_code", String(100), ForeignKey("auth.permissions.code", ondelete="CASCADE"), primary_key=True),
    schema=SCHEMA,
)


# Bo phan cua nhan vien (cot users.department). Khi co module Nhan su se noi sang ho so.
DEPARTMENTS = {
    "lab": "Kỹ thuật",
    "hr": "Nhân sự",
    "accounting": "Kế toán",
    "warehouse": "Kho",
    "delivery": "Điều phối xe",
    "office": "Văn phòng",
}


class User(Base):
    __tablename__ = "users"
    # Email / ma nhan vien chi can khong trung giua cac tai khoan CON dung: xoa mem
    # xong thi dung lai duoc cho nguoi khac.
    __table_args__ = (
        Index("ix_users_email", "email", unique=True, postgresql_where=text("deleted_at IS NULL")),
        Index("ix_users_employee_code", "employee_code", unique=True, postgresql_where=text("deleted_at IS NULL")),
        {"schema": SCHEMA},
    )

    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False)             # luu chu thuong
    employee_code = Column(String(20))                      # ma nhan vien (vd DL0123) - dang nhap bang ma nay cung duoc
    department = Column(String(30))                         # khoa trong DEPARTMENTS
    full_name = Column(String(150), nullable=False)
    password_hash = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)   # False = bi khoa han, khong dang nhap duoc

    # Khoa tam khi sai mat khau nhieu lan
    failed_logins = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True))

    # 2FA (TOTP - app Authenticator). pending: da quet QR nhung chua nhap ma xac nhan
    totp_secret = Column(String(64))
    totp_secret_pending = Column(String(64))
    totp_enabled = Column(Boolean, nullable=False, default=False)
    backup_codes = Column(JSONB, nullable=False, default=list)   # hash cua 10 ma du phong, dung xong thi xoa

    # Dat lai mat khau / doi mat khau thi tang len -> moi phien cu het hieu luc
    token_version = Column(Integer, nullable=False, default=0)
    must_change_password = Column(Boolean, nullable=False, default=False)   # MK tam do admin cap

    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))   # xoa mem: an khoi danh sach, khong dang nhap duoc

    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")


class Role(_InSchema, Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)     # admin, lab, warehouse...
    name = Column(String(100), nullable=False)                 # ten hien thi
    description = Column(Text)
    require_2fa = Column(Boolean, nullable=False, default=False)
    is_system = Column(Boolean, nullable=False, default=False)  # vai tro co san, khong xoa duoc

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, lazy="selectin")


class Permission(_InSchema, Base):
    __tablename__ = "permissions"

    code = Column(String(100), primary_key=True)     # lab.test_processes.update, hoac "*"
    module = Column(String(30), nullable=False)
    description = Column(String(255), nullable=False)


class RefreshToken(_InSchema, Base):
    """Mot phien dang nhap (mot trinh duyet). Luu hash, khong luu token that."""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    # "Ghi nho thiet bi": True -> cookie song 30 ngay; False -> cookie mat khi tat trinh duyet
    remember = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime(timezone=True))
    user_agent = Column(String(255))
    ip = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PasswordReset(_InSchema, Base):
    """Link dat lai mat khau gui qua email - dung mot lan, het han sau 30 phut."""
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
