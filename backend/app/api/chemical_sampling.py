from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas
from app.api.common import apply_payload, get_or_404

router = APIRouter(prefix="/api/chemical-sampling", tags=["chemical_sampling"])

NOT_FOUND = "Khong tim thay ban ghi lay mau"


@router.get("", response_model=list[schemas.ChemicalSamplingOut])
def list_sampling(db: Session = Depends(get_db)):
    return db.query(models.ChemicalSampling).all()


@router.post("", response_model=schemas.ChemicalSamplingOut)
def create_sampling(payload: schemas.ChemicalSamplingCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.CompanyProduct, payload.company_product_id, "Khong tim thay san pham cong ty")
    sampling = models.ChemicalSampling(**payload.model_dump())
    db.add(sampling)
    db.commit()
    db.refresh(sampling)
    return sampling


@router.put("/{sampling_id}", response_model=schemas.ChemicalSamplingOut)
def update_sampling(sampling_id: int, payload: schemas.ChemicalSamplingUpdate, db: Session = Depends(get_db)):
    sampling = get_or_404(db, models.ChemicalSampling, sampling_id, NOT_FOUND)
    apply_payload(sampling, payload)
    db.commit()
    db.refresh(sampling)
    return sampling


@router.delete("/{sampling_id}")
def delete_sampling(sampling_id: int, db: Session = Depends(get_db)):
    sampling = get_or_404(db, models.ChemicalSampling, sampling_id, NOT_FOUND)
    db.delete(sampling)
    db.commit()
    return {"ok": True}
