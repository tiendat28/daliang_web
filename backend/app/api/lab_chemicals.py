from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/lab-chemicals", tags=["lab_chemicals"])


@router.get("", response_model=list[schemas.LabChemicalOut])
def list_lab_chemicals(db: Session = Depends(get_db)):
    return db.query(models.LabChemical).all()


@router.post("", response_model=schemas.LabChemicalOut)
def create_lab_chemical(payload: schemas.LabChemicalCreate, db: Session = Depends(get_db)):
    if db.query(models.LabChemical).filter(models.LabChemical.code == payload.code).first():
        raise HTTPException(400, "Ma hoa chat da ton tai")
    data = payload.model_dump()
    remaining_volume = data.pop("remaining_volume", None)
    total_volume = (data["box_count"] or 0) * (data["volume_per_box"] or 0)
    if remaining_volume is None:
        remaining_volume = data["volume_per_box"] or 0
    chemical = models.LabChemical(**data, total_volume=total_volume, remaining_volume=remaining_volume)
    db.add(chemical)
    db.commit()
    db.refresh(chemical)
    return chemical


@router.put("/{chemical_id}", response_model=schemas.LabChemicalOut)
def update_lab_chemical(chemical_id: int, payload: schemas.LabChemicalUpdate, db: Session = Depends(get_db)):
    chemical = db.query(models.LabChemical).get(chemical_id)
    if not chemical:
        raise HTTPException(404, "Khong tim thay hoa chat")
    data = payload.model_dump()
    remaining_volume = data.pop("remaining_volume", None)
    for k, v in data.items():
        setattr(chemical, k, v)
    chemical.total_volume = (chemical.box_count or 0) * (chemical.volume_per_box or 0)
    if remaining_volume is not None:
        chemical.remaining_volume = remaining_volume
    db.commit()
    db.refresh(chemical)
    return chemical


@router.post("/{chemical_id}/open-box", response_model=schemas.LabChemicalOut)
def open_new_box(chemical_id: int, db: Session = Depends(get_db)):
    """Mo hop moi: tru 1 hop trong kho, reset phan 'le' ve dung tich 1 hop."""
    chemical = db.query(models.LabChemical).get(chemical_id)
    if not chemical:
        raise HTTPException(404, "Khong tim thay hoa chat")
    if (chemical.box_count or 0) <= 0:
        raise HTTPException(400, "Da het hop trong kho")
    chemical.box_count -= 1
    chemical.remaining_volume = chemical.volume_per_box or 0
    chemical.total_volume = (chemical.box_count or 0) * (chemical.volume_per_box or 0)
    db.commit()
    db.refresh(chemical)
    return chemical


@router.delete("/{chemical_id}")
def delete_lab_chemical(chemical_id: int, db: Session = Depends(get_db)):
    chemical = db.query(models.LabChemical).get(chemical_id)
    if not chemical:
        raise HTTPException(404, "Khong tim thay hoa chat")
    db.delete(chemical)
    db.commit()
    return {"ok": True}
