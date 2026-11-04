"""Du lieu vao/ra cua website cong khai."""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.schemas import ORM_CONFIG
from app.modules.common.schemas import WebGroup


# ---------- Website cong khai ----------
# Chi la hinh dang tra ra cho khach - khong co bang rieng: san pham lay tu
# company_products, thong tin cong ty tu company_profile, giay to tu documents.
# Moi truong chu tra ca ba thu tieng (x.vi / x.en / x.zh) de website doi ngon
# ngu ngay tai trinh duyet, khong phai goi lai API.

class Translated(BaseModel):
    vi: Optional[str] = None
    en: Optional[str] = None
    zh: Optional[str] = None


class PublicMode(BaseModel):
    name: str
    params: List[str] = []


class PublicProductOut(BaseModel):
    code: str
    group: WebGroup
    name: Translated
    desc: Translated
    materials: Optional[str] = None
    modes: List[PublicMode] = []
    msds_id: Optional[int] = None   # id trong bang documents - FE tu dung link tai
    tds_id: Optional[int] = None


class PublicLookupOut(BaseModel):
    """Ket qua tra cuu MSDS/TDS - tim tren ca danh muc, khong chi ma dang len web."""
    code: str
    name: Optional[Translated] = None
    msds_id: Optional[int] = None
    tds_id: Optional[int] = None


class PublicCertificateOut(BaseModel):
    id: int
    title: str


class PublicCompanyOut(BaseModel):
    name: Translated
    address: Translated
    tax_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    hours: Translated
    map_query: Optional[str] = None


class PublicSiteOut(BaseModel):
    company: PublicCompanyOut
    products: List[PublicProductOut]
    certificates: List[PublicCertificateOut]


class ContactLeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    company: Optional[str] = Field(default=None, max_length=255)
    phone: str = Field(min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, max_length=150)
    product: Optional[str] = Field(default=None, max_length=255)
    message: Optional[str] = None
    lang: Literal["vi", "en", "zh"] = "vi"
    source_path: Optional[str] = Field(default=None, max_length=255)

    @field_validator("name", "phone")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Không được để trống")
        return value.strip()


class ContactLeadHandledIn(BaseModel):
    is_handled: bool


class ContactLeadOut(ContactLeadCreate):
    id: int
    is_handled: bool = False
    created_at: Optional[datetime] = None
    model_config = ORM_CONFIG
