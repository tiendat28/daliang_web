"""Du lieu dieu phoi xe: doi xe, tai xe, chuyen giao hang."""
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base

SCHEMA = "dispatch"


class _InSchema:
    __table_args__ = {"schema": SCHEMA}


class Vehicle(_InSchema, Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    plate_number = Column(String(50), nullable=False, unique=True)  # 51C-892.14, 51D-452.19, 60C-338.90
    vehicle_type = Column(String(50), nullable=False, default="Xe tải 1.5 tấn")
    max_payload_kg = Column(Numeric(10, 2), default=1500)
    hazard_permit_expiry = Column(Date)  # Giay phep van chuyen hang nguy hiem
    status = Column(String(30), nullable=False, default="active")  # active, maintenance, inactive
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    drivers = relationship("Driver", back_populates="default_vehicle")
    trips = relationship("DeliveryTrip", back_populates="vehicle")


class Driver(_InSchema, Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("auth.users.id", ondelete="SET NULL"))
    full_name = Column(String(100), nullable=False)  # Đỗ Thành Long, Mai Huy, Trịnh Khoa, Phan Lực, Võ Sơn
    phone = Column(String(20))
    license_number = Column(String(50))
    license_class = Column(String(20), default="C")
    hazard_training_expiry = Column(Date)
    default_vehicle_id = Column(Integer, ForeignKey("dispatch.vehicles.id", ondelete="SET NULL"))
    status = Column(String(30), nullable=False, default="ready")  # running, ready, issue, off
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    default_vehicle = relationship("Vehicle", back_populates="drivers")
    trips = relationship("DeliveryTrip", back_populates="driver")


class DeliveryTrip(_InSchema, Base):
    __tablename__ = "delivery_trips"

    id = Column(Integer, primary_key=True)
    trip_code = Column(String(50), nullable=False, unique=True)  # CG-2609-01
    dispatch_code = Column(String(50), nullable=False)  # PX-2609-14
    dispatch_order_id = Column(Integer, ForeignKey("warehouse.dispatches.id", ondelete="SET NULL"))
    customer_name = Column(String(200), nullable=False)
    customer_address = Column(String(255))
    items_summary = Column(String(255))
    is_hazardous = Column(Boolean, nullable=False, default=True)  # Hang nguy hiem
    driver_id = Column(Integer, ForeignKey("dispatch.drivers.id", ondelete="SET NULL"))
    vehicle_id = Column(Integer, ForeignKey("dispatch.vehicles.id", ondelete="SET NULL"))
    status = Column(String(30), nullable=False, default="unassigned")  # unassigned, delivering, delivered, issue
    estimated_time = Column(String(50))  # 10:40, 11:15
    delivered_at = Column(DateTime(timezone=True))
    proof_image_url = Column(String(255))  # Anh bien nhan
    issue_note = Column(Text)  # Khach vang — hen lai
    trip_date = Column(Date, nullable=False)
    created_by = Column(Integer, ForeignKey("auth.users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    driver = relationship("Driver", back_populates="trips")
    vehicle = relationship("Vehicle", back_populates="trips")
