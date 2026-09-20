from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas
from app.services import inventory
from app.api.common import apply_payload, get_or_404

router = APIRouter(prefix="/api/chemical-orders", tags=["chemical_orders"])

NOT_FOUND = "Khong tim thay don hang"
CHEMICAL_NOT_FOUND = "Khong tim thay hoa chat PTN"


@router.get("", response_model=list[schemas.ChemicalOrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.ChemicalOrder).all()


@router.post("", response_model=schemas.ChemicalOrderOut)
def create_order(payload: schemas.ChemicalOrderCreate, db: Session = Depends(get_db)):
    lab_chemical = get_or_404(db, models.LabChemical, payload.lab_chemical_id, CHEMICAL_NOT_FOUND)
    get_or_404(db, models.Customer, payload.customer_id, "Khong tim thay khach hang")

    order = models.ChemicalOrder(**payload.model_dump())
    db.add(order)
    inventory.deduct_lab_chemical(db, lab_chemical, payload.used_amount)
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_id}", response_model=schemas.ChemicalOrderOut)
def update_order(order_id: int, payload: schemas.ChemicalOrderUpdate, db: Session = Depends(get_db)):
    order = get_or_404(db, models.ChemicalOrder, order_id, NOT_FOUND)

    # Hoan lai luong cua dong cu roi tru theo dong moi (don co the doi sang hoa chat khac)
    old_lab_chemical = db.get(models.LabChemical, order.lab_chemical_id)
    if old_lab_chemical:
        inventory.restore_lab_chemical(db, old_lab_chemical, order.used_amount)

    new_lab_chemical = get_or_404(db, models.LabChemical, payload.lab_chemical_id, CHEMICAL_NOT_FOUND)
    apply_payload(order, payload)
    inventory.deduct_lab_chemical(db, new_lab_chemical, payload.used_amount)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = get_or_404(db, models.ChemicalOrder, order_id, NOT_FOUND)
    lab_chemical = db.get(models.LabChemical, order.lab_chemical_id)
    if lab_chemical:
        inventory.restore_lab_chemical(db, lab_chemical, order.used_amount)
    db.delete(order)
    db.commit()
    return {"ok": True}
