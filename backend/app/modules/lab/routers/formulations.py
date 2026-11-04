from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.crud import apply_payload, get_or_404
from app.core.database import get_db
from app.modules.common import models as common_models
from app.modules.lab import models, schemas
from app.modules.lab.services import inventory

router = APIRouter(prefix="/formulations", tags=["formulations"])

NOT_FOUND = "Không tìm thấy đơn hàng"
CHEMICAL_NOT_FOUND = "Không tìm thấy hóa chất PTN"


@router.get("", response_model=list[schemas.ChemicalOrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.ChemicalOrder).all()


@router.post("", response_model=schemas.ChemicalOrderOut)
def create_order(payload: schemas.ChemicalOrderCreate, db: Session = Depends(get_db)):
    lab_chemical = get_or_404(db, models.LabChemical, payload.lab_chemical_id, CHEMICAL_NOT_FOUND)
    get_or_404(db, common_models.Customer, payload.customer_id, "Không tìm thấy khách hàng")

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
