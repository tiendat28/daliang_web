"""Pydantic schemas cho module dieu phoi xe."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class VehicleBase(BaseModel):
    plate_number: str
    vehicle_type: str = "Xe tải 1.5 tấn"
    max_payload_kg: float = 1500
    hazard_permit_expiry: Optional[date] = None
    status: str = "active"
    notes: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleOut(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DriverBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    license_number: Optional[str] = None
    license_class: str = "C"
    hazard_training_expiry: Optional[date] = None
    default_vehicle_id: Optional[int] = None
    status: str = "ready"  # running, ready, issue, off


class DriverCreate(DriverBase):
    user_id: Optional[int] = None


class DriverOut(DriverBase):
    id: int
    default_vehicle_plate: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeliveryTripBase(BaseModel):
    dispatch_code: str
    customer_name: str
    customer_address: Optional[str] = None
    items_summary: Optional[str] = None
    is_hazardous: bool = True
    status: str = "unassigned"  # unassigned, delivering, delivered, issue
    estimated_time: Optional[str] = None
    issue_note: Optional[str] = None
    trip_date: date


class DeliveryTripCreate(BaseModel):
    trip_code: Optional[str] = None
    dispatch_code: str
    dispatch_order_id: Optional[int] = None
    customer_name: str
    customer_address: Optional[str] = None
    items_summary: Optional[str] = None
    is_hazardous: bool = True
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    estimated_time: Optional[str] = None
    trip_date: date = Field(default_factory=date.today)


class DeliveryTripAssign(BaseModel):
    driver_id: int
    vehicle_id: Optional[int] = None
    estimated_time: Optional[str] = None


class DeliveryTripStatusUpdate(BaseModel):
    status: str  # delivering, delivered, issue
    issue_note: Optional[str] = None
    proof_image_url: Optional[str] = None
    estimated_time: Optional[str] = None


class DeliveryTripOut(DeliveryTripBase):
    id: int
    trip_code: str
    dispatch_order_id: Optional[int] = None
    driver_id: Optional[int] = None
    driver_name: Optional[str] = None
    driver_initials: Optional[str] = None
    vehicle_id: Optional[int] = None
    vehicle_plate: Optional[str] = None
    delivered_at: Optional[datetime] = None
    proof_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DispatchDashboardMetrics(BaseModel):
    trips_today: int = 6
    delivering_count: int = 2
    delivered_count: int = 1
    issues_count: int = 1


class TripsByStatus(BaseModel):
    unassigned: list[DeliveryTripOut] = Field(default_factory=list)
    delivering: list[DeliveryTripOut] = Field(default_factory=list)
    delivered: list[DeliveryTripOut] = Field(default_factory=list)
    issue: list[DeliveryTripOut] = Field(default_factory=list)


class DispatchDashboardOut(BaseModel):
    metrics: DispatchDashboardMetrics
    drivers: list[DriverOut]
    trips: TripsByStatus
