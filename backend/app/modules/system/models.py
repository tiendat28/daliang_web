"""Module he thong (schema `system`): nhat ky thao tac.

Tai khoan / vai tro nam o module auth; module system chi co trang quan ly
(router) va nhat ky.
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base

SCHEMA = "system"


class AuditLog(Base):
    """Moi thao tac ghi (them/sua/xoa) va moi su kien dang nhap - ai, luc nao, lam gi.

    Khong luu noi dung body (co the chua mat khau, file).
    """
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(Integer, ForeignKey("auth.users.id", ondelete="SET NULL"), index=True)
    user_email = Column(String(150))      # chot lai ten luc ghi - xoa user van doc duoc nhat ky
    action = Column(String(60), nullable=False, index=True)   # "PUT", "DELETE", "login.success", "2fa.enable"...
    module = Column(String(30), index=True)
    path = Column(String(255))
    status = Column(Integer)
    ip = Column(String(64))
    summary = Column(String(255))         # cau de doc: "Sửa đơn hàng HCTN #5", "Khoá tài khoản An"
    detail = Column(JSONB)
