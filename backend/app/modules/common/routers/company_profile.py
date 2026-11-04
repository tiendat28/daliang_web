"""Thong tin cong ty - letterhead cua moi phieu in + lien he tren website.

Bang chi co dung 1 dong nen khong co route theo id - GET/PUT deu lam viec voi
dong duy nhat do. Khung xem truoc letterhead dung template to in nen nam o
module lab (POST /api/v1/lab/test-processes/letterhead-preview).
"""
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import API_PREFIX, STATIC_DIR
from app.core.database import get_db
from app.modules.common import models, schemas
from app.modules.common.services.company_profile import COMPANY_PROFILE, get_or_create_profile

router = APIRouter(prefix="/company-profile", tags=["company-profile"])

LOGO_DIR = STATIC_DIR / "img"
MAX_LOGO_BYTES = 2 * 1024 * 1024
ALLOWED_LOGO_TYPES = {"image/png": ".png", "image/jpeg": ".jpg"}



def _profile_out(profile: models.CompanyProfile) -> schemas.CompanyProfileOut:
    out = schemas.CompanyProfileOut.model_validate(profile)
    out.logo_url = f"{API_PREFIX}/static/{profile.logo_path.lstrip('/')}" if profile.logo_path else None
    return out


@router.get("", response_model=schemas.CompanyProfileOut)
def get_company_profile(db: Session = Depends(get_db)):
    return _profile_out(get_or_create_profile(db))


@router.put("", response_model=schemas.CompanyProfileOut)
def update_company_profile(payload: schemas.CompanyProfileUpdate, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db)
    # Chi ghi truong client gui len: bang nay dung chung cho phieu in va website,
    # form nao cung chi gui phan cua minh.
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return _profile_out(profile)



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

    profile = get_or_create_profile(db)
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
