"""Du lieu vao/ra cua du lieu dung chung (schema `common`)."""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, field_validator

from app.core.schemas import ORM_CONFIG
from app.modules.common.models import DocumentCategory


# ---------- Customer ----------
class CustomerFieldProductOut(BaseModel):
    id: int
    product_code_text: Optional[str] = None
    company_product_id: Optional[int] = None
    model_config = ORM_CONFIG


class CustomerFieldOut(BaseModel):
    id: int
    field_name: str
    products: List[CustomerFieldProductOut] = []
    model_config = ORM_CONFIG


class CustomerFieldIn(BaseModel):
    field_name: str
    product_codes: List[str] = []  # se tu map sang company_products neu trung ma


class CustomerBase(BaseModel):
    name: str
    address: Optional[str] = None
    note: Optional[str] = None


class CustomerCreate(CustomerBase):
    fields: List[CustomerFieldIn] = []


class CustomerUpdate(CustomerBase):
    fields: List[CustomerFieldIn] = []


class CustomerOut(CustomerBase):
    id: int
    fields: List[CustomerFieldOut] = []
    model_config = ORM_CONFIG


# ---------- Company Product ----------
class CompanyProductModeBase(BaseModel):
    name: str = "Chung"                  # "Thep - Nhung nong", "Mạ treo (Rack)"
    params: List[str] = []               # moi phan tu mot dong "Nhiet do: 50-75 oC"

    # Form gui len o ten che do de trong -> coi la che do "Chung"; dong thong so
    # trong thi bo, de khong in ra dong rong tren the san pham.
    @field_validator("name", mode="before")
    @classmethod
    def _blank_name_is_general(cls, value):
        return (value or "").strip() or "Chung"

    @field_validator("params", mode="before")
    @classmethod
    def _drop_blank_params(cls, value):
        return [str(p).strip() for p in (value or []) if str(p or "").strip()]


class CompanyProductModeOut(CompanyProductModeBase):
    id: int
    model_config = ORM_CONFIG


# Nhom tren website (cot company_products.web_group): Tien xu ly / Phu gia ma / Thu dong
WebGroup = Literal["pre", "add", "pas"]


class CompanyProductBase(BaseModel):
    code: str
    name: str
    name_en: Optional[str] = None
    category: Optional[str] = None
    usage_stage: Optional[str] = None
    materials: Optional[str] = None
    description: Optional[str] = None
    # Website cong khai: web_group de trong = ma khong len web
    name_zh: Optional[str] = None
    description_en: Optional[str] = None
    description_zh: Optional[str] = None
    web_group: Optional[WebGroup] = None


class CompanyProductWrite(CompanyProductBase):
    modes: List[CompanyProductModeBase] = []


class CompanyProductCreate(CompanyProductWrite):
    pass


class CompanyProductUpdate(CompanyProductWrite):
    pass


class CompanyProductWebsiteIn(BaseModel):
    """Chi phan hien tren website - truong nao khong gui thi giu nguyen."""
    web_group: Optional[WebGroup] = None
    name_zh: Optional[str] = None
    description_en: Optional[str] = None
    description_zh: Optional[str] = None


class CompanyProductOut(CompanyProductBase):
    id: int
    modes: List[CompanyProductModeOut] = []
    model_config = ORM_CONFIG


# ---------- Document (Tai lieu) ----------
class DocumentOut(BaseModel):
    id: int
    category: DocumentCategory
    name: str
    original_filename: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    model_config = ORM_CONFIG


# ---------- Letterhead ----------
class CompanyProfileBase(BaseModel):
    name_zh: Optional[str] = None
    name_en: Optional[str] = None
    address_zh: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    # Chi website dung
    name_vi: Optional[str] = None
    address_vi: Optional[str] = None
    tax_id: Optional[str] = None
    email: Optional[str] = None
    hours_vi: Optional[str] = None
    hours_en: Optional[str] = None
    hours_zh: Optional[str] = None
    map_query: Optional[str] = None


class CompanyProfileUpdate(CompanyProfileBase):
    pass


class CompanyProfileOut(CompanyProfileBase):
    id: int
    logo_path: Optional[str] = None
    logo_url: Optional[str] = None
    model_config = ORM_CONFIG
