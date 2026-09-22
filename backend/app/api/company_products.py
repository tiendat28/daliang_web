from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app import models, schemas
from app.api.common import apply_payload, get_or_404
from app.core.product_catalog import build_modes

router = APIRouter(prefix="/api/company-products", tags=["company_products"])

NOT_FOUND = "Khong tim thay san pham"


@router.get("", response_model=list[schemas.CompanyProductOut])
def list_products(db: Session = Depends(get_db)):
    return (
        db.query(models.CompanyProduct)
        .options(joinedload(models.CompanyProduct.modes))
        .order_by(models.CompanyProduct.code)
        .all()
    )


@router.post("", response_model=schemas.CompanyProductOut)
def create_product(payload: schemas.CompanyProductCreate, db: Session = Depends(get_db)):
    if db.query(models.CompanyProduct).filter(models.CompanyProduct.code == payload.code).first():
        raise HTTPException(400, "Ma san pham da ton tai")
    data = payload.model_dump()
    modes = build_modes(data.pop("modes"))
    product = models.CompanyProduct(**data, modes=modes)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=schemas.CompanyProductOut)
def update_product(product_id: int, payload: schemas.CompanyProductUpdate, db: Session = Depends(get_db)):
    product = get_or_404(db, models.CompanyProduct, product_id, NOT_FOUND)
    duplicate = db.query(models.CompanyProduct).filter(
        models.CompanyProduct.code == payload.code, models.CompanyProduct.id != product_id,
    ).first()
    if duplicate:
        raise HTTPException(400, "Ma san pham da ton tai")
    apply_payload(product, payload, exclude={"modes"})
    product.modes = build_modes(payload.model_dump()["modes"])
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_or_404(db, models.CompanyProduct, product_id, NOT_FOUND)
    db.delete(product)
    db.commit()
    return {"ok": True}
