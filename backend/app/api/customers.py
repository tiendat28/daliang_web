from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/customers", tags=["customers"])


def _sync_fields(db: Session, customer: models.Customer, fields_in):
    for f in list(customer.fields):
        db.delete(f)
    db.flush()

    for f_in in fields_in:
        field = models.CustomerField(field_name=f_in.field_name, customer=customer)
        db.add(field)
        db.flush()
        for code in f_in.product_codes:
            code = code.strip()
            if not code:
                continue
            product = db.query(models.CompanyProduct).filter(models.CompanyProduct.code == code).first()
            db.add(models.CustomerFieldProduct(
                customer_field_id=field.id,
                company_product_id=product.id if product else None,
                product_code_text=code,
            ))


@router.get("", response_model=list[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).options(
        joinedload(models.Customer.fields).joinedload(models.CustomerField.products)
    ).all()


@router.get("/{customer_id}", response_model=schemas.CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).get(customer_id)
    if not customer:
        raise HTTPException(404, "Khong tim thay khach hang")
    return customer


@router.post("", response_model=schemas.CustomerOut)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    customer = models.Customer(name=payload.name, address=payload.address, note=payload.note)
    db.add(customer)
    db.flush()
    _sync_fields(db, customer, payload.fields)
    db.commit()
    db.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=schemas.CustomerOut)
def update_customer(customer_id: int, payload: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).get(customer_id)
    if not customer:
        raise HTTPException(404, "Khong tim thay khach hang")
    customer.name = payload.name
    customer.address = payload.address
    customer.note = payload.note
    _sync_fields(db, customer, payload.fields)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).get(customer_id)
    if not customer:
        raise HTTPException(404, "Khong tim thay khach hang")
    db.delete(customer)
    db.commit()
    return {"ok": True}
