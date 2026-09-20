from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas
from app.api.common import apply_payload, get_or_404

router = APIRouter(prefix="/api/lab-chemicals", tags=["lab_chemicals"])

NOT_FOUND = "Khong tim thay hoa chat"


def _total_volume(chemical: models.LabChemical) -> float:
    """Tong luong hang nguyen hop = so hop x dung tich moi hop."""
    return (chemical.box_count or 0) * (chemical.volume_per_box or 0)


@router.get("", response_model=list[schemas.LabChemicalOut])
def list_lab_chemicals(db: Session = Depends(get_db)):
    return db.query(models.LabChemical).all()


@router.post("", response_model=schemas.LabChemicalOut)
def create_lab_chemical(payload: schemas.LabChemicalCreate, db: Session = Depends(get_db)):
    if db.query(models.LabChemical).filter_by(code=payload.code).first():
        raise HTTPException(400, "Ma hoa chat da ton tai")
    data = payload.model_dump()
    remaining_volume = data.pop("remaining_volume", None)
    if remaining_volume is None:  # chua nhap phan le -> coi nhu dang dung 1 hop nguyen
        remaining_volume = data["volume_per_box"] or 0
    chemical = models.LabChemical(**data, remaining_volume=remaining_volume)
    chemical.total_volume = _total_volume(chemical)
    db.add(chemical)
    db.commit()
    db.refresh(chemical)
    return chemical


@router.put("/{chemical_id}", response_model=schemas.LabChemicalOut)
def update_lab_chemical(chemical_id: int, payload: schemas.LabChemicalUpdate, db: Session = Depends(get_db)):
    chemical = get_or_404(db, models.LabChemical, chemical_id, NOT_FOUND)
    remaining_volume = payload.remaining_volume
    apply_payload(chemical, payload, exclude={"remaining_volume"})
    chemical.total_volume = _total_volume(chemical)
    if remaining_volume is not None:
        chemical.remaining_volume = remaining_volume
    db.commit()
    db.refresh(chemical)
    return chemical


@router.post("/{chemical_id}/open-box", response_model=schemas.LabChemicalOut)
def open_new_box(chemical_id: int, db: Session = Depends(get_db)):
    """Mo hop moi: tru 1 hop trong kho, reset phan 'le' ve dung tich 1 hop."""
    chemical = get_or_404(db, models.LabChemical, chemical_id, NOT_FOUND)
    if (chemical.box_count or 0) <= 0:
        raise HTTPException(400, "Da het hop trong kho")
    chemical.box_count -= 1
    chemical.remaining_volume = chemical.volume_per_box or 0
    chemical.total_volume = _total_volume(chemical)
    db.commit()
    db.refresh(chemical)
    return chemical


@router.delete("/{chemical_id}")
def delete_lab_chemical(chemical_id: int, db: Session = Depends(get_db)):
    chemical = get_or_404(db, models.LabChemical, chemical_id, NOT_FOUND)
    db.delete(chemical)
    db.commit()
    return {"ok": True}
