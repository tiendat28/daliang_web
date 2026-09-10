from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/chemical-sampling", tags=["chemical_sampling"])


@router.get("", response_model=list[schemas.ChemicalSamplingOut])
def list_sampling(db: Session = Depends(get_db)):
    return db.query(models.ChemicalSampling).all()


@router.post("", response_model=schemas.ChemicalSamplingOut)
def create_sampling(payload: schemas.ChemicalSamplingCreate, db: Session = Depends(get_db)):
    if not db.query(models.CompanyProduct).get(payload.company_product_id):
        raise HTTPException(404, "Khong tim thay san pham cong ty")
    sampling = models.ChemicalSampling(**payload.model_dump())
    db.add(sampling)
    db.commit()
    db.refresh(sampling)
    return sampling


@router.put("/{sampling_id}", response_model=schemas.ChemicalSamplingOut)
def update_sampling(sampling_id: int, payload: schemas.ChemicalSamplingUpdate, db: Session = Depends(get_db)):
    sampling = db.query(models.ChemicalSampling).get(sampling_id)
    if not sampling:
        raise HTTPException(404, "Khong tim thay ban ghi lay mau")
    for k, v in payload.model_dump().items():
        setattr(sampling, k, v)
    db.commit()
    db.refresh(sampling)
    return sampling


@router.delete("/{sampling_id}")
def delete_sampling(sampling_id: int, db: Session = Depends(get_db)):
    sampling = db.query(models.ChemicalSampling).get(sampling_id)
    if not sampling:
        raise HTTPException(404, "Khong tim thay ban ghi lay mau")
    db.delete(sampling)
    db.commit()
    return {"ok": True}
