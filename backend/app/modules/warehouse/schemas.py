"""Pydantic schemas cho module quan ly kho."""
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    warehouse_name: str
    code: str
    zone: Optional[str] = None
    shelf: Optional[str] = None
    bin: Optional[str] = None
    note: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationOut(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockItemBase(BaseModel):
    product_code: str
    product_name: str
    category: str = "finished"  # finished, material, packaging
    lot_number: str
    expiration_date: Optional[date] = None
    location_code: str
    quantity: float = 0
    unit: str = "kg"
    hazard_types: Optional[str] = None
    min_threshold: float = 0
    max_capacity: float = 500
    note: Optional[str] = None


class StockItemCreate(StockItemBase):
    product_id: Optional[int] = None
    location_id: Optional[int] = None


class StockItemUpdate(BaseModel):
    quantity: Optional[float] = None
    location_code: Optional[str] = None
    expiration_date: Optional[date] = None
    min_threshold: Optional[float] = None
    note: Optional[str] = None


class StockItemOut(StockItemBase):
    id: int
    stock_percent: Optional[float] = None
    is_low_stock: Optional[bool] = None
    is_expiring_soon: Optional[bool] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReceiptItemBase(BaseModel):
    product_code: str
    product_name: str
    category: str = "material"
    lot_number: str
    expiration_date: Optional[date] = None
    location_code: Optional[str] = None
    quantity: float = 1
    unit: str = "kg"
    hazard_types: Optional[str] = None


class ReceiptItemCreate(ReceiptItemBase):
    pass


class ReceiptItemOut(ReceiptItemBase):
    id: int
    receipt_id: int

    model_config = ConfigDict(from_attributes=True)


class ReceiptCreate(BaseModel):
    receipt_code: Optional[str] = None
    receipt_type: str = "purchase"
    supplier_name: Optional[str] = None
    receipt_date: date
    note: Optional[str] = None
    items: list[ReceiptItemCreate] = Field(default_factory=list)


class ReceiptOut(BaseModel):
    id: int
    receipt_code: str
    receipt_type: str
    supplier_name: Optional[str]
    receipt_date: date
    status: str
    note: Optional[str]
    items: list[ReceiptItemOut] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DispatchItemBase(BaseModel):
    product_code: str
    product_name: str
    lot_number: Optional[str] = None
    quantity: float = 1
    unit: str = "kg"
    status: str = "pending"


class DispatchItemCreate(DispatchItemBase):
    pass


class DispatchItemOut(DispatchItemBase):
    id: int
    dispatch_id: int

    model_config = ConfigDict(from_attributes=True)


class DispatchCreate(BaseModel):
    dispatch_code: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: str
    dispatch_date: date
    items_summary: Optional[str] = None
    receiver_name: Optional[str] = None
    driver_name: Optional[str] = None
    vehicle_plate: Optional[str] = None
    note: Optional[str] = None
    items: list[DispatchItemCreate] = Field(default_factory=list)


class DispatchLoadRequest(BaseModel):
    driver_name: str
    vehicle_plate: str
    note: Optional[str] = None


class DispatchOut(BaseModel):
    id: int
    dispatch_code: str
    customer_id: Optional[int]
    customer_name: str
    dispatch_date: date
    status: str
    items_summary: Optional[str]
    receiver_name: Optional[str]
    driver_name: Optional[str]
    vehicle_plate: Optional[str]
    note: Optional[str]
    items: list[DispatchItemOut] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditBase(BaseModel):
    audit_code: Optional[str] = None
    warehouse_name: str
    audit_date: date
    status: str = "completed"
    auditor_name: Optional[str] = None
    note: Optional[str] = None


class AuditCreate(AuditBase):
    pass


class AuditOut(AuditBase):
    id: int
    audit_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseDashboardMetrics(BaseModel):
    total_items: int = 136
    warehouses_count: int = 3
    locations_count: int = 48
    low_stock_count: int = 4
    expiring_count: int = 6
    today_dispatches_count: int = 9
    pending_dispatches_count: int = 3


class WarehouseAlertItem(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    badge: str
    badge_type: str  # red, purple, blue, amber


class WarehouseDashboardOut(BaseModel):
    metrics: WarehouseDashboardMetrics
    stock_lots: list[StockItemOut]
    pending_dispatches: list[DispatchOut]
    alerts: list[WarehouseAlertItem]
