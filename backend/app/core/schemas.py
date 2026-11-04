"""Cau hinh Pydantic dung chung cho moi module."""
from pydantic import ConfigDict

# Cac schema *Out doc thang tu doi tuong SQLAlchemy
ORM_CONFIG = ConfigDict(from_attributes=True)
