from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("", response_model=list[schemas.IndicatorOut])
def list_indicators(db: Session = Depends(get_db)):
    return db.query(models.Indicator).all()


@router.post("", response_model=schemas.IndicatorOut)
def create_indicator(payload: schemas.IndicatorCreate, db: Session = Depends(get_db)):
    indicator = models.Indicator(**payload.model_dump())
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator


@router.put("/{indicator_id}", response_model=schemas.IndicatorOut)
def update_indicator(indicator_id: int, payload: schemas.IndicatorUpdate, db: Session = Depends(get_db)):
    indicator = db.query(models.Indicator).get(indicator_id)
    if not indicator:
        raise HTTPException(404, "Khong tim thay chat chi thi")
    for k, v in payload.model_dump().items():
        setattr(indicator, k, v)
    db.commit()
    db.refresh(indicator)
    return indicator


@router.delete("/{indicator_id}")
def delete_indicator(indicator_id: int, db: Session = Depends(get_db)):
    indicator = db.query(models.Indicator).get(indicator_id)
    if not indicator:
        raise HTTPException(404, "Khong tim thay chat chi thi")
    db.delete(indicator)
    db.commit()
    return {"ok": True}
