"""API cho website cong khai (daliang.com) - phan khach hang nhin thay.

Khong co bang rieng cho website, chi doc lai du lieu noi bo va chon phan duoc
phep cong khai:
  - san pham: company_products co web_group (thong so lay tu company_product_modes)
  - thong tin lien he: company_profile (dong duy nhat, dung chung voi letterhead)
  - chung nhan: documents loai "certificate"
  - link MSDS / TDS cua tung ma: file loai "msds" / "technical" trong documents
    co ma san pham trong ten; file mo qua /public/files (chi 3 loai cong khai)
Rieng form lien he ghi vao website.contact_leads.
"""
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.modules.common import models as common_models
from app.modules.common.services.company_profile import get_or_create_profile
from app.modules.auth.deps import guard
from app.modules.common.services.documents import document_response
from app.modules.website import models, schemas

Category = common_models.DocumentCategory

router = APIRouter(prefix="/website")

# Phan khach hang goi, khong can dang nhap - /api/v1/website/public/...
public = APIRouter(prefix="/public", tags=["website-public"])
# Phan nguoi trong cong ty xem (don khach gui) - /api/v1/website/contact-leads
leads = APIRouter(prefix="/contact-leads", tags=["website-contact-leads"],
                  dependencies=[Depends(guard("website.contact_leads"))])

# Loai tai lieu khach duoc tai qua website. Tai lieu noi bo khac (COA, phuong
# phap phan tich) chi mo qua /api/v1/common/documents.
PUBLIC_CATEGORIES = (Category.msds, Category.technical, Category.certificate)

GROUP_ORDER = case({"pre": 0, "add": 1, "pas": 2}, value=common_models.CompanyProduct.web_group)


def _translated(vi, en=None, zh=None) -> schemas.Translated:
    return schemas.Translated(vi=vi, en=en, zh=zh)


def _company_out(profile: common_models.CompanyProfile) -> schemas.PublicCompanyOut:
    return schemas.PublicCompanyOut(
        name=_translated(profile.name_vi, profile.name_en, profile.name_zh),
        # Chua co dia chi tieng Anh: trang en dung ban tieng Viet
        address=_translated(profile.address_vi, profile.address_vi, profile.address_zh),
        tax_id=profile.tax_id,
        phone=profile.phone,
        email=profile.email,
        hours=_translated(profile.hours_vi, profile.hours_en, profile.hours_zh),
        map_query=profile.map_query,
    )


def _code_pattern(code: str) -> re.Pattern:
    """Ma nam trong ten file: "MSDS NCZ-48.pdf" khop NCZ-48, "NCZ-480" thi khong."""
    return re.compile(rf"(?<![A-Z0-9]){re.escape(code.upper())}(?!\d)")


def _latest_file_by_code(docs: list, code: str) -> int | None:
    pattern = _code_pattern(code)
    for doc_id, name, filename in docs:   # docs da sap moi nhat truoc
        if pattern.search(f"{name} {filename}".upper()):
            return doc_id
    return None


def _document_index(db: Session, category: common_models.DocumentCategory) -> list:
    """(id, ten, ten file) cua mot loai tai lieu - khong tai cot content (file)."""
    return (
        db.query(common_models.Document.id, common_models.Document.name, common_models.Document.original_filename)
        .filter(common_models.Document.category == category)
        .order_by(common_models.Document.uploaded_at.desc())
        .all()
    )


def _product_out(product: common_models.CompanyProduct, msds_docs: list, tds_docs: list) -> schemas.PublicProductOut:
    return schemas.PublicProductOut(
        code=product.code,
        group=product.web_group,
        name=_translated(product.name, product.name_en, product.name_zh),
        desc=_translated(product.description, product.description_en, product.description_zh),
        materials=product.materials,
        modes=[schemas.PublicMode(name=m.name, params=m.params or []) for m in product.modes],
        msds_id=_latest_file_by_code(msds_docs, product.code),
        tds_id=_latest_file_by_code(tds_docs, product.code),
    )


@public.get("/site", response_model=schemas.PublicSiteOut)
def get_site(db: Session = Depends(get_db)):
    """Toan bo noi dung website trong mot lan goi - trang nao cung can ca ba phan."""
    products = (
        db.query(common_models.CompanyProduct)
        .options(joinedload(common_models.CompanyProduct.modes))
        .filter(common_models.CompanyProduct.web_group.isnot(None))
        .order_by(GROUP_ORDER, common_models.CompanyProduct.id)
        .all()
    )
    msds_docs = _document_index(db, Category.msds)
    tds_docs = _document_index(db, Category.technical)
    certificates = (
        db.query(common_models.Document.id, common_models.Document.name)
        .filter(common_models.Document.category == Category.certificate)
        .order_by(common_models.Document.uploaded_at)
        .all()
    )
    return schemas.PublicSiteOut(
        company=_company_out(get_or_create_profile(db)),
        products=[_product_out(p, msds_docs, tds_docs) for p in products],
        certificates=[schemas.PublicCertificateOut(id=c.id, title=c.name) for c in certificates],
    )


@public.get("/lookup/{code}", response_model=schemas.PublicLookupOut | None)
def lookup_documents(code: str, db: Session = Depends(get_db)):
    """O "Tra cuu MSDS / TDS": ma nao cung tra duoc, ke ca ma khong len web.
    Khong co ca san pham lan file nao thi tra null (trang tu bao "khong tim thay")."""
    code = " ".join(code.split()).upper()
    product = db.query(common_models.CompanyProduct).filter(common_models.CompanyProduct.code.ilike(code)).first()
    msds_id = _latest_file_by_code(_document_index(db, Category.msds), code)
    tds_id = _latest_file_by_code(_document_index(db, Category.technical), code)
    if not (product or msds_id or tds_id):
        return None
    return schemas.PublicLookupOut(
        code=product.code if product else code,
        name=_translated(product.name, product.name_en, product.name_zh) if product else None,
        msds_id=msds_id,
        tds_id=tds_id,
    )


@public.post("/contact-leads", response_model=schemas.ContactLeadOut, status_code=201)
def create_contact_lead(payload: schemas.ContactLeadCreate, db: Session = Depends(get_db)):
    """Form "Nhan bao gia" tren web - route ghi duy nhat, khong can dang nhap."""
    lead = models.ContactLead(**payload.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@leads.get("", response_model=list[schemas.ContactLeadOut])
def list_contact_leads(db: Session = Depends(get_db)):
    return db.query(models.ContactLead).order_by(models.ContactLead.id.desc()).all()


@leads.patch("/{lead_id}", response_model=schemas.ContactLeadOut)
def mark_contact_lead(lead_id: int, data: schemas.ContactLeadHandledIn, db: Session = Depends(get_db)):
    """Danh dau da xu ly / chua xu ly."""
    lead = db.get(models.ContactLead, lead_id)
    if lead is None:
        raise HTTPException(404, "Không tìm thấy đơn")
    lead.is_handled = data.is_handled
    db.commit()
    return lead


@public.get("/files/{document_id}")
def get_public_file(document_id: int, db: Session = Depends(get_db)):
    """Mo file MSDS / TDS / ban scan giay to tu website."""
    doc = db.get(common_models.Document, document_id)
    if doc is None or doc.category not in PUBLIC_CATEGORIES:
        raise HTTPException(404, "Không tìm thấy tài liệu")
    return document_response(doc, inline=True)


router.include_router(public)
router.include_router(leads)
