"""Du lieu dung chung cua ca cong ty (schema `common`).

Khach hang, san pham, thong tin cong ty, tai lieu: moi bo phan (ky thuat,
kho, ke toan, website) tham chieu toi day, khong chep ban rieng. Bang o day
KHONG tro nguoc sang bang cua module khac.
"""
import enum

from sqlalchemy import (
    Column, DateTime, Enum, ForeignKey, Integer, LargeBinary, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

SCHEMA = "common"


class _InSchema:
    __table_args__ = {"schema": SCHEMA}


class DocumentCategory(str, enum.Enum):
    msds = "msds"                            # MSDS
    coa = "coa"                              # COA
    technical = "technical"                  # Ky thuat
    method_analysis = "method_analysis"      # Phuong phap phan tich
    certificate = "certificate"              # Chung nhan / giay to phap ly - hien tren website


class Customer(_InSchema, Base):
    """Bang 1: KH"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255))
    note = Column(Text)

    fields = relationship("CustomerField", back_populates="customer", cascade="all, delete-orphan")


class CustomerField(_InSchema, Base):
    """Linh vuc cua tung KH (1 KH - n linh vuc)"""
    __tablename__ = "customer_fields"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("common.customers.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(255), nullable=False)

    customer = relationship("Customer", back_populates="fields")
    products = relationship("CustomerFieldProduct", back_populates="customer_field", cascade="all, delete-orphan")


class CustomerFieldProduct(_InSchema, Base):
    """SP dung theo tung linh vuc (n SP dung / linh vuc), co gang map sang company_products theo ma"""
    __tablename__ = "customer_field_products"

    id = Column(Integer, primary_key=True, index=True)
    customer_field_id = Column(Integer, ForeignKey("common.customer_fields.id", ondelete="CASCADE"), nullable=False)
    company_product_id = Column(Integer, ForeignKey("common.company_products.id", ondelete="SET NULL"), nullable=True)
    product_code_text = Column(String(100))

    customer_field = relationship("CustomerField", back_populates="products")
    company_product = relationship("CompanyProduct")


class CompanyProduct(_InSchema, Base):
    """Bang 2: SP Cty - danh muc san pham, nap tu app/data/company_products.json."""
    __tablename__ = "company_products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)   # ten tieng Viet
    name_en = Column(String(255))
    category = Column(String(255))                # Nhom phan loai
    usage_stage = Column(String(255))             # Giai doan su dung
    materials = Column(String(255))               # Vat lieu ap dung
    description = Column(Text)                    # Cong dung

    # Rieng cho website cong khai. Nap lai danh muc tu JSON khong dung toi cac
    # cot nay (product_catalog._apply chi ghi cac cot cua file Excel).
    name_zh = Column(String(255))
    description_en = Column(Text)
    description_zh = Column(Text)
    web_group = Column(String(10), index=True)   # pre | add | pas; NULL = khong len web

    modes = relationship(
        "CompanyProductMode", back_populates="product",
        cascade="all, delete-orphan", order_by="CompanyProductMode.position",
    )


class CompanyProductMode(_InSchema, Base):
    """Mot che do su dung cua san pham (vd "Thep - Nhung nong") kem bang thong so van hanh.

    Ma chi co mot cach dung thi co dung mot che do "Chung". Thong so la chu tu do,
    moi phan tu mot dong, dang "Nhiet do: 50-75 oC" - de nguyen van nhu tai lieu
    nha cung cap vi moi ma ghi mot kieu, khong tach duoc thanh cot co dinh.
    """
    __tablename__ = "company_product_modes"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("common.company_products.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    params = Column(JSONB, nullable=False, default=list)

    product = relationship("CompanyProduct", back_populates="modes")


class Document(_InSchema, Base):
    """Tai lieu (MSDS, CO/A, Ky thuat, Phieu huy)"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Enum(DocumentCategory), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    content = Column(LargeBinary)   # noi dung file luu thang trong DB (o dia container bi xoa moi lan deploy)
    mime_type = Column(String(150))
    file_size = Column(Integer)
    uploaded_by = Column(String(150))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class CompanyProfile(_InSchema, Base):
    """Thong tin cong ty - bang chi co dung 1 dong (id = 1).

    Dung chung cho letterhead cua moi phieu in va phan lien he cua website.
    """
    __tablename__ = "company_profile"

    id = Column(Integer, primary_key=True, index=True)
    logo_path = Column(String(255))       # duong dan tuong doi trong app/static
    name_zh = Column(String(255))
    name_en = Column(String(255))
    address_zh = Column(String(255))
    phone = Column(String(100))
    fax = Column(String(100))

    # Chi website dung (phieu in chi co ten Trung/Anh)
    name_vi = Column(String(255))
    address_vi = Column(String(255))
    tax_id = Column(String(100))
    email = Column(String(150))
    hours_vi = Column(String(255))
    hours_en = Column(String(255))
    hours_zh = Column(String(255))
    map_query = Column(String(500))       # de trong = khung ban do hien o cho
