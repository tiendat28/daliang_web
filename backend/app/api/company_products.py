from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/company-products", tags=["company_products"])


@router.get("", response_model=list[schemas.CompanyProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.CompanyProduct).all()


@router.post("", response_model=schemas.CompanyProductOut)
def create_product(payload: schemas.CompanyProductCreate, db: Session = Depends(get_db)):
    if db.query(models.CompanyProduct).filter(models.CompanyProduct.code == payload.code).first():
        raise HTTPException(400, "Ma san pham da ton tai")
    product = models.CompanyProduct(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=schemas.CompanyProductOut)
def update_product(product_id: int, payload: schemas.CompanyProductUpdate, db: Session = Depends(get_db)):
    product = db.query(models.CompanyProduct).get(product_id)
    if not product:
        raise HTTPException(404, "Khong tim thay san pham")
    for k, v in payload.model_dump().items():
        setattr(product, k, v)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.CompanyProduct).get(product_id)
    if not product:
        raise HTTPException(404, "Khong tim thay san pham")
    db.delete(product)
    db.commit()
    return {"ok": True}
