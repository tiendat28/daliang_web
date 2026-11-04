"""Smoke test cho module Dieu phoi xe (Dispatch)."""
from datetime import date
from decimal import Decimal
import pytest

from app.modules.dispatch import models, schemas
from app.modules.dispatch.router import _initials


def test_dispatch_helpers_and_schemas_in_memory():
    assert _initials("Đỗ Thành Long") == "ĐT"
    assert _initials("Mai Huy") == "MH"
    assert _initials("Trịnh Khoa") == "TK"
    assert _initials("Phan Lực") == "PL"
    assert _initials("Võ Sơn") == "VS"

    v = schemas.VehicleOut(
        id=1,
        plate_number="51C-892.14",
        vehicle_type="Xe tải 1.5 tấn",
        max_payload_kg=1500.0,
        hazard_permit_expiry=date(2026, 10, 20),
        status="active",
        notes=None,
        created_at=date.today(),
        updated_at=date.today(),
    )
    assert v.plate_number == "51C-892.14"

    d = schemas.DriverOut(
        id=1,
        full_name="Đỗ Thành Long",
        phone="0908 123 456",
        license_class="C",
        status="running",
        default_vehicle_plate="51C-892.14",
        created_at=date.today(),
        updated_at=date.today(),
    )
    assert d.status == "running"

    t = schemas.DeliveryTripOut(
        id=1,
        trip_code="CG-2609-14",
        dispatch_code="PX-2609-14",
        customer_name="Xi mạ Tân Phú",
        items_summary="4 can NI-534C · 2 can CU-4",
        is_hazardous=True,
        status="unassigned",
        trip_date=date.today(),
        created_at=date.today(),
        updated_at=date.today(),
    )
    assert t.is_hazardous is True
    assert t.status == "unassigned"

    dash = schemas.DispatchDashboardOut(
        metrics=schemas.DispatchDashboardMetrics(
            trips_today=6,
            delivering_count=2,
            delivered_count=1,
            issues_count=1,
        ),
        drivers=[d],
        trips=schemas.TripsByStatus(
            unassigned=[t],
            delivering=[],
            delivered=[],
            issue=[],
        ),
    )
    assert dash.metrics.trips_today == 6
    assert len(dash.trips.unassigned) == 1


def test_dispatch_db_flow(db_session):
    # Tao xe
    veh = models.Vehicle(
        plate_number="51C-892.14",
        vehicle_type="Xe tải 1.5 tấn",
        max_payload_kg=Decimal("1500"),
        status="active",
    )
    db_session.add(veh)
    db_session.flush()

    # Tao tai xe
    driver = models.Driver(
        full_name="Đỗ Thành Long",
        default_vehicle_id=veh.id,
        status="ready",
    )
    db_session.add(driver)
    db_session.flush()

    # Tao chuyen giao
    trip = models.DeliveryTrip(
        trip_code="CG-2609-14",
        dispatch_code="PX-2609-14",
        customer_name="Xi mạ Tân Phú",
        items_summary="4 can NI-534C",
        status="unassigned",
        trip_date=date.today(),
    )
    db_session.add(trip)
    db_session.flush()
    assert trip.id is not None

    # Phan cong tai xe
    trip.driver_id = driver.id
    trip.vehicle_id = veh.id
    trip.status = "delivering"
    driver.status = "running"
    db_session.flush()

    assert trip.status == "delivering"
    assert driver.status == "running"
