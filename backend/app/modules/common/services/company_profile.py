"""Nghiep vu dung chung: thong tin cong ty (bang company_profile, dung 1 dong).

Mot dong nay dung cho ca letterhead cua phieu in (module lab) lan phan lien
he cua website - hai noi doc cung mot ban, khong chep.
"""
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.modules.common import models

# Gia tri mac dinh. Ma so thue va email chua biet nen de nguyen ngoac vuong -
# nhin thay tren web la biet phai dien (trang Cai dat cua cong noi bo).
COMPANY_PROFILE = {
    "logo_path": "img/logo-dlvc.png",
    "name_zh": "越南大亮化工有限公司",
    "name_en": "DALIANG CHEMICAL VIETNAM CO.,LTD",
    "address_zh": "越南平陽省新淵縣帝國社帝國工業區 D2 路",
    "phone": "0650-3651005~09",
    "fax": "0650-3651010",
    "name_vi": "Công ty TNHH Hóa chất Daliang VN",
    "address_vi": "Đường D2, KCN Đất Cuốc, huyện Bắc Tân Uyên, tỉnh Bình Dương",
    "tax_id": "[Mã số thuế]",
    "email": "[email@daliang.com]",
    "hours_vi": "Thứ 2 – Thứ 7, 7:30 – 17:00",
    "hours_en": "Mon – Sat, 7:30 – 17:00",
    "hours_zh": "周一至周六 7:30 – 17:00",
}


def get_or_create_profile(db: Session) -> models.CompanyProfile:
    profile = db.query(models.CompanyProfile).order_by(models.CompanyProfile.id).first()
    if not profile:
        profile = models.CompanyProfile(**COMPANY_PROFILE)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def seed_company_profile(engine: Engine) -> None:
    """Luc khoi dong: tao dong neu chua co, co roi thi chi dien o con trong
    (khong de len noi dung nguoi dung da sua)."""
    with Session(engine) as db:
        profile = get_or_create_profile(db)
        for key, value in COMPANY_PROFILE.items():
            if getattr(profile, key) in (None, ""):
                setattr(profile, key, value)
        db.commit()
