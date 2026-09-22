from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app import models, schemas
from app.api.common import apply_payload, get_or_404

router = APIRouter(prefix="/api/company-products", tags=["company_products"])

NOT_FOUND = "Khong tim thay san pham"


def _sync_components(db: Session, product: models.CompanyProduct, components_in):
    """Dung lai ca bang thong so; form gui len bao nhieu dong thi giu bay nhieu."""
    for component in list(product.components):
        db.delete(component)
    db.flush()
    for component_in in components_in:
        db.add(models.CompanyProductComponent(
            product_id=product.id,
            component=component_in.component,
            standard=component_in.standard,
            spec_range=component_in.spec_range,
        ))


@router.get("", response_model=list[schemas.CompanyProductOut])
def list_products(db: Session = Depends(get_db)):
    return (
        db.query(models.CompanyProduct)
        .options(joinedload(models.CompanyProduct.components))
        .order_by(models.CompanyProduct.id)
        .all()
    )


@router.post("", response_model=schemas.CompanyProductOut)
def create_product(payload: schemas.CompanyProductCreate, db: Session = Depends(get_db)):
    if db.query(models.CompanyProduct).filter(models.CompanyProduct.code == payload.code).first():
        raise HTTPException(400, "Ma san pham da ton tai")
    product = models.CompanyProduct(**payload.model_dump(exclude={"components"}))
    db.add(product)
    db.flush()
    _sync_components(db, product, payload.components)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=schemas.CompanyProductOut)
def update_product(product_id: int, payload: schemas.CompanyProductUpdate, db: Session = Depends(get_db)):
    product = get_or_404(db, models.CompanyProduct, product_id, NOT_FOUND)
    apply_payload(product, payload, exclude={"components"})
    _sync_components(db, product, payload.components)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_or_404(db, models.CompanyProduct, product_id, NOT_FOUND)
    db.delete(product)
    db.commit()
    return {"ok": True}
