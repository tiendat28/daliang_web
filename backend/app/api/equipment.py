from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


def _sync_variants(db: Session, equipment: models.Equipment, variants_in):
    for v in list(equipment.variants):
        db.delete(v)
    db.flush()
    for v_in in variants_in:
        db.add(models.EquipmentVariant(
            equipment_id=equipment.id,
            classification=v_in.classification,
            quantity=v_in.quantity,
            unit=v_in.unit,
            note=v_in.note,
        ))


@router.get("", response_model=list[schemas.EquipmentOut])
def list_equipment(db: Session = Depends(get_db)):
    return db.query(models.Equipment).options(joinedload(models.Equipment.variants)).order_by(models.Equipment.id).all()


@router.post("", response_model=schemas.EquipmentOut)
def create_equipment(payload: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    equipment = models.Equipment(name=payload.name, note=payload.note)
    db.add(equipment)
    db.flush()
    _sync_variants(db, equipment, payload.variants)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.put("/{equipment_id}", response_model=schemas.EquipmentOut)
def update_equipment(equipment_id: int, payload: schemas.EquipmentUpdate, db: Session = Depends(get_db)):
    equipment = db.query(models.Equipment).get(equipment_id)
    if not equipment:
        raise HTTPException(404, "Khong tim thay thiet bi")
    equipment.name = payload.name
    equipment.note = payload.note
    _sync_variants(db, equipment, payload.variants)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.delete("/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(models.Equipment).get(equipment_id)
    if not equipment:
        raise HTTPException(404, "Khong tim thay thiet bi")
    db.delete(equipment)
    db.commit()
    return {"ok": True}
