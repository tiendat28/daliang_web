"""Tien ich dung chung cho cac router CRUD."""
from typing import TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


def get_or_404(db: Session, model: type[ModelT], obj_id: int, message: str) -> ModelT:
    """Lay ban ghi theo id, khong co thi tra 404 kem thong bao tieng Viet."""
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(404, message)
    return obj


def apply_payload(obj: ModelT, payload: BaseModel, exclude: set[str] | None = None) -> ModelT:
    """Gan cac truong cua payload vao ban ghi (dung cho PUT)."""
    for key, value in payload.model_dump(exclude=exclude or set()).items():
        setattr(obj, key, value)
    return obj
