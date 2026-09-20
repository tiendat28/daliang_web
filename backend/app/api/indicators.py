from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas
from app.api.common import apply_payload, get_or_404

router = APIRouter(prefix="/api/indicators", tags=["indicators"])

NOT_FOUND = "Khong tim thay chat chi thi"


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
    indicator = get_or_404(db, models.Indicator, indicator_id, NOT_FOUND)
    apply_payload(indicator, payload)
    db.commit()
    db.refresh(indicator)
    return indicator


@router.delete("/{indicator_id}")
def delete_indicator(indicator_id: int, db: Session = Depends(get_db)):
    indicator = get_or_404(db, models.Indicator, indicator_id, NOT_FOUND)
    db.delete(indicator)
    db.commit()
    return {"ok": True}
