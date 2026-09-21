"""Thong tin letterhead in tren dau moi phieu.

Bang chi co dung 1 dong, dung chung cho cac phieu in khac ve sau, nen khong co
route theo id - GET/PUT deu lam viec voi dong duy nhat do.
"""
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.database import get_db
from app.core.seed import COMPANY_PROFILE
from app.services.test_process_sheet import STATIC_DIR, render_sheet_html

router = APIRouter(prefix="/api/company-profile", tags=["company-profile"])

LOGO_DIR = STATIC_DIR / "img"
MAX_LOGO_BYTES = 2 * 1024 * 1024
ALLOWED_LOGO_TYPES = {"image/png": ".png", "image/jpeg": ".jpg"}


def _get_or_create(db: Session) -> models.CompanyProfile:
    profile = db.query(models.CompanyProfile).order_by(models.CompanyProfile.id).first()
    if not profile:
        profile = models.CompanyProfile(**COMPANY_PROFILE)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def _profile_out(profile: models.CompanyProfile) -> schemas.CompanyProfileOut:
    out = schemas.CompanyProfileOut.model_validate(profile)
    out.logo_url = f"/api/static/{profile.logo_path.lstrip('/')}" if profile.logo_path else None
    return out


@router.get("", response_model=schemas.CompanyProfileOut)
def get_company_profile(db: Session = Depends(get_db)):
    return _profile_out(_get_or_create(db))


@router.put("", response_model=schemas.CompanyProfileOut)
def update_company_profile(payload: schemas.CompanyProfileUpdate, db: Session = Depends(get_db)):
    profile = _get_or_create(db)
    for key, value in payload.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return _profile_out(profile)


@router.post("/preview", response_class=HTMLResponse)
def preview_letterhead(payload: schemas.CompanyProfileUpdate, db: Session = Depends(get_db)):
    """To phieu rong voi letterhead dang go (chua luu) - cho khung xem truoc.

    Dung chung template voi ban PDF nen sua o day thay ngay dung cai se in ra.
    """
    current = _get_or_create(db)
    profile = {
        "logo_path": current.logo_path,   # logo doi bang route rieng, khong nam trong form
        **payload.model_dump(),
    }
    # To rong: build_sheet_context tu dien mac dinh cho moi truong con thieu
    return HTMLResponse(render_sheet_html({}, profile, screen=True))


@router.post("/logo", response_model=schemas.CompanyProfileOut)
async def upload_logo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    extension = ALLOWED_LOGO_TYPES.get(file.content_type or "")
    if not extension:
        raise HTTPException(400, "Logo chỉ nhận file PNG hoặc JPG")

    data = await file.read()
    if len(data) > MAX_LOGO_BYTES:
        raise HTTPException(400, "Logo tối đa 2MB, vui lòng chọn ảnh nhẹ hơn")
    if not data:
        raise HTTPException(400, "File logo rỗng")

    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    # Ten ngau nhien de trinh duyet khong dung lai ban cu trong cache
    filename = f"logo-{uuid.uuid4().hex}{extension}"
    (LOGO_DIR / filename).write_bytes(data)

    profile = _get_or_create(db)
    previous = profile.logo_path
    profile.logo_path = f"img/{filename}"
    db.commit()
    db.refresh(profile)

    # Xoa file cu, tru anh goc di kem repo (con dung lam gia tri mac dinh)
    if previous and previous != COMPANY_PROFILE["logo_path"]:
        old_path = STATIC_DIR / previous.lstrip("/")
        if old_path.is_file() and str(old_path.resolve()).startswith(str(LOGO_DIR.resolve())):
            os.remove(old_path)

    return _profile_out(profile)
