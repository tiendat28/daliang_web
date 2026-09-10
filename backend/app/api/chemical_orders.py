from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas
from app.services import inventory

router = APIRouter(prefix="/api/chemical-orders", tags=["chemical_orders"])


@router.get("", response_model=list[schemas.ChemicalOrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.ChemicalOrder).all()


@router.post("", response_model=schemas.ChemicalOrderOut)
def create_order(payload: schemas.ChemicalOrderCreate, db: Session = Depends(get_db)):
    lab_chemical = db.query(models.LabChemical).get(payload.lab_chemical_id)
    if not lab_chemical:
        raise HTTPException(404, "Khong tim thay hoa chat PTN")
    if not db.query(models.Customer).get(payload.customer_id):
        raise HTTPException(404, "Khong tim thay khach hang")

    order = models.ChemicalOrder(**payload.model_dump())
    db.add(order)
    inventory.deduct_lab_chemical(db, lab_chemical, payload.used_amount)
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_id}", response_model=schemas.ChemicalOrderOut)
def update_order(order_id: int, payload: schemas.ChemicalOrderUpdate, db: Session = Depends(get_db)):
    order = db.query(models.ChemicalOrder).get(order_id)
    if not order:
        raise HTTPException(404, "Khong tim thay don hang")

    old_lab_chemical = db.query(models.LabChemical).get(order.lab_chemical_id)
    if old_lab_chemical:
        inventory.restore_lab_chemical(db, old_lab_chemical, order.used_amount)

    new_lab_chemical = db.query(models.LabChemical).get(payload.lab_chemical_id)
    if not new_lab_chemical:
        raise HTTPException(404, "Khong tim thay hoa chat PTN")

    for k, v in payload.model_dump().items():
        setattr(order, k, v)

    inventory.deduct_lab_chemical(db, new_lab_chemical, payload.used_amount)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.ChemicalOrder).get(order_id)
    if not order:
        raise HTTPException(404, "Khong tim thay don hang")
    lab_chemical = db.query(models.LabChemical).get(order.lab_chemical_id)
    if lab_chemical:
        inventory.restore_lab_chemical(db, lab_chemical, order.used_amount)
    db.delete(order)
    db.commit()
    return {"ok": True}
