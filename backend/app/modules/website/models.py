"""Website cong khai (schema `website`).

Noi dung web (san pham, lien he, giay to) doc tu `common` - chi bang cua
rieng website nam o day.
"""
from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Text, func,
)

from app.core.database import Base

SCHEMA = "website"


class _InSchema:
    __table_args__ = {"schema": SCHEMA}


class ContactLead(_InSchema, Base):
    """Mot luot gui form "Nhan bao gia" tren website."""
    __tablename__ = "contact_leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    phone = Column(String(100), nullable=False)
    email = Column(String(150))
    product = Column(String(255))        # o "San pham quan tam"
    message = Column(Text)
    lang = Column(String(5))             # ngon ngu khach dang xem: vi | en | zh
    source_path = Column(String(255))    # URL luc gui, de biet trang nao ra don
    is_handled = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
