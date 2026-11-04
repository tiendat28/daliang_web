"""Du lieu quan ly kho: ton kho theo lo, phieu nhap, phieu xuat, vi tri, kiem ke."""
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base

SCHEMA = "warehouse"


class _InSchema:
    __table_args__ = {"schema": SCHEMA}


class Location(_InSchema, Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    warehouse_name = Column(String(100), nullable=False)  # Kho A - Thành phẩm, Kho B - Nguyên liệu, Kho C - Bao bì
    code = Column(String(50), nullable=False, unique=True)  # A-02-3, B-01-1, C-01-4
    zone = Column(String(50))
    shelf = Column(String(50))
    bin = Column(String(50))
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class StockItem(_InSchema, Base):
    __tablename__ = "stock_items"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("common.company_products.id", ondelete="SET NULL"))
    product_code = Column(String(50), nullable=False)  # NI-534C, CRT-650, CU-4, NL-NaOH
    product_name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, default="finished")  # finished (Thành phẩm), material (Nguyên liệu), packaging (Bao bì)
    lot_number = Column(String(50), nullable=False)  # L2609-02, N2607-01
    expiration_date = Column(Date)
    location_id = Column(Integer, ForeignKey("warehouse.locations.id", ondelete="SET NULL"))
    location_code = Column(String(50), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False, default=0)
    unit = Column(String(30), nullable=False, default="kg")
    hazard_types = Column(String(200))  # toxic, corrosive, oxidizing, etc. (comma separated or json)
    min_threshold = Column(Numeric(12, 2), nullable=False, default=0)
    max_capacity = Column(Numeric(12, 2), nullable=False, default=500)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Receipt(_InSchema, Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True)
    receipt_code = Column(String(50), nullable=False, unique=True)  # PN-2609-01
    receipt_type = Column(String(30), nullable=False, default="purchase")  # purchase / production / return
    supplier_name = Column(String(200))
    receipt_date = Column(Date, nullable=False)
    status = Column(String(30), nullable=False, default="completed")  # draft / completed / cancelled
    note = Column(Text)
    created_by = Column(Integer, ForeignKey("auth.users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")


class ReceiptItem(_InSchema, Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True)
    receipt_id = Column(Integer, ForeignKey("warehouse.receipts.id", ondelete="CASCADE"), nullable=False)
    product_code = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, default="material")
    lot_number = Column(String(50), nullable=False)
    expiration_date = Column(Date)
    location_code = Column(String(50))
    quantity = Column(Numeric(12, 2), nullable=False, default=1)
    unit = Column(String(30), nullable=False, default="kg")
    hazard_types = Column(String(200))

    receipt = relationship("Receipt", back_populates="items")


class Dispatch(_InSchema, Base):
    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True)
    dispatch_code = Column(String(50), nullable=False, unique=True)  # PX-2609-14
    customer_id = Column(Integer, ForeignKey("common.customers.id", ondelete="SET NULL"))
    customer_name = Column(String(200), nullable=False)
    dispatch_date = Column(Date, nullable=False)
    status = Column(String(30), nullable=False, default="pending")  # pending (Chờ soạn) / picked (Đã soạn) / loaded (Đã giao xe) / delivered (Đã hoàn thành)
    items_summary = Column(String(255))
    receiver_name = Column(String(100))
    driver_name = Column(String(100))
    vehicle_plate = Column(String(50))
    note = Column(Text)
    created_by = Column(Integer, ForeignKey("auth.users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items = relationship("DispatchItem", back_populates="dispatch", cascade="all, delete-orphan")


class DispatchItem(_InSchema, Base):
    __tablename__ = "dispatch_items"

    id = Column(Integer, primary_key=True)
    dispatch_id = Column(Integer, ForeignKey("warehouse.dispatches.id", ondelete="CASCADE"), nullable=False)
    product_code = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    lot_number = Column(String(50))
    quantity = Column(Numeric(12, 2), nullable=False, default=1)
    unit = Column(String(30), nullable=False, default="kg")
    status = Column(String(30), nullable=False, default="pending")

    dispatch = relationship("Dispatch", back_populates="items")


class Audit(_InSchema, Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True)
    audit_code = Column(String(50), nullable=False, unique=True)  # KK-2609-01
    warehouse_name = Column(String(100), nullable=False)
    audit_date = Column(Date, nullable=False)
    status = Column(String(30), nullable=False, default="completed")  # in_progress / completed
    auditor_name = Column(String(100))
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
