from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.crud import apply_payload, get_or_404
from app.core.database import get_db
from app.modules.common import models as common_models
from app.modules.lab import models, schemas

router = APIRouter(prefix="/samples", tags=["samples"])

NOT_FOUND = "Không tìm thấy bản ghi lấy mẫu"


@router.get("", response_model=list[schemas.ChemicalSamplingOut])
def list_sampling(db: Session = Depends(get_db)):
    return db.query(models.ChemicalSampling).all()


@router.post("", response_model=schemas.ChemicalSamplingOut)
def create_sampling(payload: schemas.ChemicalSamplingCreate, db: Session = Depends(get_db)):
    get_or_404(db, common_models.CompanyProduct, payload.company_product_id, "Không tìm thấy sản phẩm công ty")
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
