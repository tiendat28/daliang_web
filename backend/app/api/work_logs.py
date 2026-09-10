from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/work-logs", tags=["work_logs"])


@router.get("", response_model=list[schemas.WorkLogOut])
def list_work_logs(db: Session = Depends(get_db)):
    return db.query(models.WorkLog).all()


@router.post("", response_model=schemas.WorkLogOut)
def create_work_log(payload: schemas.WorkLogCreate, db: Session = Depends(get_db)):
    entry = models.WorkLog(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/{entry_id}", response_model=schemas.WorkLogOut)
def update_work_log(entry_id: int, payload: schemas.WorkLogUpdate, db: Session = Depends(get_db)):
    entry = db.query(models.WorkLog).get(entry_id)
    if not entry:
        raise HTTPException(404, "Khong tim thay nhat ky")
    for k, v in payload.model_dump().items():
        setattr(entry, k, v)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}")
def delete_work_log(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(models.WorkLog).get(entry_id)
    if not entry:
        raise HTTPException(404, "Khong tim thay nhat ky")
    db.delete(entry)
    db.commit()
    return {"ok": True}
