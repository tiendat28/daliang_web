"""API router cho module Dieu phoi giao hang va quan ly doi xe (Dispatch)."""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.modules.auth.deps import get_current_user, guard
from app.modules.auth.models import User
from app.modules.dispatch import models, schemas

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


def _initials(name: str) -> str:
    if not name:
        return ""
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return parts[0][:2].upper()


@router.get("/dashboard", response_model=schemas.DispatchDashboardOut, dependencies=[Depends(guard("dispatch.trips"))])
def get_dispatch_dashboard(
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Tong quan bang dieu phoi: KPI, doi xe/tai xe va 4 cot Kanban."""
    # Drivers with vehicle
    drivers_db = (
        db.query(models.Driver)
        .options(joinedload(models.Driver.default_vehicle))
        .order_by(models.Driver.id.asc())
        .all()
    )
    drivers = []
    for d in drivers_db:
        plate = d.default_vehicle.plate_number if d.default_vehicle else None
        drivers.append(
            schemas.DriverOut(
                id=d.id,
                full_name=d.full_name,
                phone=d.phone,
                license_number=d.license_number,
                license_class=d.license_class,
                hazard_training_expiry=d.hazard_training_expiry,
                default_vehicle_id=d.default_vehicle_id,
                default_vehicle_plate=plate,
                status=d.status,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
        )

    # Trips query
    trips_query = (
        db.query(models.DeliveryTrip)
        .options(
            joinedload(models.DeliveryTrip.driver),
            joinedload(models.DeliveryTrip.vehicle),
        )
    )
    if q:
        term = f"%{q.strip()}%"
        trips_query = trips_query.filter(
            or_(
                models.DeliveryTrip.dispatch_code.ilike(term),
                models.DeliveryTrip.customer_name.ilike(term),
                models.DeliveryTrip.items_summary.ilike(term),
                models.DeliveryTrip.customer_address.ilike(term),
            )
        )

    all_trips = trips_query.order_by(models.DeliveryTrip.id.desc()).all()

    trips_by_status = schemas.TripsByStatus()
    for t in all_trips:
        driver_name = t.driver.full_name if t.driver else None
        driver_init = _initials(driver_name) if driver_name else None
        vehicle_plate = t.vehicle.plate_number if t.vehicle else None

        trip_out = schemas.DeliveryTripOut(
            id=t.id,
            trip_code=t.trip_code,
            dispatch_code=t.dispatch_code,
            dispatch_order_id=t.dispatch_order_id,
            customer_name=t.customer_name,
            customer_address=t.customer_address,
            items_summary=t.items_summary,
            is_hazardous=t.is_hazardous,
            driver_id=t.driver_id,
            driver_name=driver_name,
            driver_initials=driver_init,
            vehicle_id=t.vehicle_id,
            vehicle_plate=vehicle_plate,
            status=t.status,
            estimated_time=t.estimated_time,
            delivered_at=t.delivered_at,
            proof_image_url=t.proof_image_url,
            issue_note=t.issue_note,
            trip_date=t.trip_date,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )

        if t.status == "unassigned":
            trips_by_status.unassigned.append(trip_out)
        elif t.status == "delivering":
            trips_by_status.delivering.append(trip_out)
        elif t.status == "delivered":
            trips_by_status.delivered.append(trip_out)
        elif t.status == "issue":
            trips_by_status.issue.append(trip_out)

    delivering_count = len(trips_by_status.delivering)
    delivered_count = len(trips_by_status.delivered)
    issues_count = len(trips_by_status.issue)
    trips_today = len(all_trips) if len(all_trips) > 0 else 6

    metrics = schemas.DispatchDashboardMetrics(
        trips_today=trips_today,
        delivering_count=delivering_count,
        delivered_count=delivered_count,
        issues_count=issues_count,
    )

    return schemas.DispatchDashboardOut(
        metrics=metrics,
        drivers=drivers,
        trips=trips_by_status,
    )


# ---------------- Trips ----------------
@router.get("/trips", response_model=list[schemas.DeliveryTripOut], dependencies=[Depends(guard("dispatch.trips"))])
def list_trips(
    status_filter: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.DeliveryTrip)
        .options(
            joinedload(models.DeliveryTrip.driver),
            joinedload(models.DeliveryTrip.vehicle),
        )
    )
    if status_filter:
        query = query.filter(models.DeliveryTrip.status == status_filter)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                models.DeliveryTrip.dispatch_code.ilike(term),
                models.DeliveryTrip.customer_name.ilike(term),
                models.DeliveryTrip.items_summary.ilike(term),
            )
        )
    trips = query.order_by(models.DeliveryTrip.id.desc()).all()
    results = []
    for t in trips:
        driver_name = t.driver.full_name if t.driver else None
        results.append(
            schemas.DeliveryTripOut(
                id=t.id,
                trip_code=t.trip_code,
                dispatch_code=t.dispatch_code,
                dispatch_order_id=t.dispatch_order_id,
                customer_name=t.customer_name,
                customer_address=t.customer_address,
                items_summary=t.items_summary,
                is_hazardous=t.is_hazardous,
                driver_id=t.driver_id,
                driver_name=driver_name,
                driver_initials=_initials(driver_name) if driver_name else None,
                vehicle_id=t.vehicle_id,
                vehicle_plate=t.vehicle.plate_number if t.vehicle else None,
                status=t.status,
                estimated_time=t.estimated_time,
                delivered_at=t.delivered_at,
                proof_image_url=t.proof_image_url,
                issue_note=t.issue_note,
                trip_date=t.trip_date,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
        )
    return results


@router.post("/trips", response_model=schemas.DeliveryTripOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(guard("dispatch.trips"))])
def create_trip(
    payload: schemas.DeliveryTripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    code = payload.trip_code
    if not code:
        count = db.query(models.DeliveryTrip).count() + 1
        code = f"CG-{date.today().strftime('%y%m')}-{count:02d}"

    st = "unassigned"
    if payload.driver_id:
        st = "delivering"

    trip = models.DeliveryTrip(
        trip_code=code,
        dispatch_code=payload.dispatch_code,
        dispatch_order_id=payload.dispatch_order_id,
        customer_name=payload.customer_name,
        customer_address=payload.customer_address,
        items_summary=payload.items_summary,
        is_hazardous=payload.is_hazardous,
        driver_id=payload.driver_id,
        vehicle_id=payload.vehicle_id,
        status=st,
        estimated_time=payload.estimated_time,
        trip_date=payload.trip_date,
        created_by=current_user.id,
    )
    db.add(trip)
    if payload.driver_id:
        driver = db.query(models.Driver).filter(models.Driver.id == payload.driver_id).first()
        if driver:
            driver.status = "running"
    db.commit()
    db.refresh(trip)

    driver_name = trip.driver.full_name if trip.driver else None
    return schemas.DeliveryTripOut(
        id=trip.id,
        trip_code=trip.trip_code,
        dispatch_code=trip.dispatch_code,
        dispatch_order_id=trip.dispatch_order_id,
        customer_name=trip.customer_name,
        customer_address=trip.customer_address,
        items_summary=trip.items_summary,
        is_hazardous=trip.is_hazardous,
        driver_id=trip.driver_id,
        driver_name=driver_name,
        driver_initials=_initials(driver_name) if driver_name else None,
        vehicle_id=trip.vehicle_id,
        vehicle_plate=trip.vehicle.plate_number if trip.vehicle else None,
        status=trip.status,
        estimated_time=trip.estimated_time,
        delivered_at=trip.delivered_at,
        proof_image_url=trip.proof_image_url,
        issue_note=trip.issue_note,
        trip_date=trip.trip_date,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
    )


@router.post("/trips/{trip_id}/assign", response_model=schemas.DeliveryTripOut, dependencies=[Depends(guard("dispatch.trips"))])
def assign_trip(
    trip_id: int,
    payload: schemas.DeliveryTripAssign,
    db: Session = Depends(get_db),
):
    trip = db.query(models.DeliveryTrip).filter(models.DeliveryTrip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến giao hàng")

    driver = db.query(models.Driver).filter(models.Driver.id == payload.driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài xế")

    trip.driver_id = driver.id
    vehicle_id = payload.vehicle_id or driver.default_vehicle_id
    trip.vehicle_id = vehicle_id
    trip.status = "delivering"
    if payload.estimated_time:
        trip.estimated_time = payload.estimated_time
    driver.status = "running"

    db.commit()
    db.refresh(trip)

    driver_name = trip.driver.full_name if trip.driver else None
    return schemas.DeliveryTripOut(
        id=trip.id,
        trip_code=trip.trip_code,
        dispatch_code=trip.dispatch_code,
        dispatch_order_id=trip.dispatch_order_id,
        customer_name=trip.customer_name,
        customer_address=trip.customer_address,
        items_summary=trip.items_summary,
        is_hazardous=trip.is_hazardous,
        driver_id=trip.driver_id,
        driver_name=driver_name,
        driver_initials=_initials(driver_name) if driver_name else None,
        vehicle_id=trip.vehicle_id,
        vehicle_plate=trip.vehicle.plate_number if trip.vehicle else None,
        status=trip.status,
        estimated_time=trip.estimated_time,
        delivered_at=trip.delivered_at,
        proof_image_url=trip.proof_image_url,
        issue_note=trip.issue_note,
        trip_date=trip.trip_date,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
    )


@router.post("/trips/{trip_id}/status", response_model=schemas.DeliveryTripOut, dependencies=[Depends(guard("dispatch.trips"))])
def update_trip_status(
    trip_id: int,
    payload: schemas.DeliveryTripStatusUpdate,
    db: Session = Depends(get_db),
):
    trip = db.query(models.DeliveryTrip).filter(models.DeliveryTrip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến giao hàng")

    trip.status = payload.status
    if payload.status == "delivered":
        trip.delivered_at = datetime.now()
        if payload.proof_image_url:
            trip.proof_image_url = payload.proof_image_url
        if trip.driver:
            trip.driver.status = "ready"
    elif payload.status == "issue":
        if payload.issue_note:
            trip.issue_note = payload.issue_note
        if trip.driver:
            trip.driver.status = "issue"
    elif payload.status == "delivering":
        if payload.estimated_time:
            trip.estimated_time = payload.estimated_time
        if trip.driver:
            trip.driver.status = "running"

    db.commit()
    db.refresh(trip)

    driver_name = trip.driver.full_name if trip.driver else None
    return schemas.DeliveryTripOut(
        id=trip.id,
        trip_code=trip.trip_code,
        dispatch_code=trip.dispatch_code,
        dispatch_order_id=trip.dispatch_order_id,
        customer_name=trip.customer_name,
        customer_address=trip.customer_address,
        items_summary=trip.items_summary,
        is_hazardous=trip.is_hazardous,
        driver_id=trip.driver_id,
        driver_name=driver_name,
        driver_initials=_initials(driver_name) if driver_name else None,
        vehicle_id=trip.vehicle_id,
        vehicle_plate=trip.vehicle.plate_number if trip.vehicle else None,
        status=trip.status,
        estimated_time=trip.estimated_time,
        delivered_at=trip.delivered_at,
        proof_image_url=trip.proof_image_url,
        issue_note=trip.issue_note,
        trip_date=trip.trip_date,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
    )


# ---------------- Vehicles & Drivers ----------------
@router.get("/vehicles", response_model=list[schemas.VehicleOut], dependencies=[Depends(guard("dispatch.vehicles"))])
def list_vehicles(db: Session = Depends(get_db)):
    return db.query(models.Vehicle).order_by(models.Vehicle.id.asc()).all()


@router.post("/vehicles", response_model=schemas.VehicleOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(guard("dispatch.vehicles"))])
def create_vehicle(
    payload: schemas.VehicleCreate,
    db: Session = Depends(get_db),
):
    vehicle = models.Vehicle(
        plate_number=payload.plate_number,
        vehicle_type=payload.vehicle_type,
        max_payload_kg=payload.max_payload_kg,
        hazard_permit_expiry=payload.hazard_permit_expiry,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/drivers", response_model=list[schemas.DriverOut], dependencies=[Depends(guard("dispatch.drivers"))])
def list_drivers(db: Session = Depends(get_db)):
    drivers = db.query(models.Driver).options(joinedload(models.Driver.default_vehicle)).order_by(models.Driver.id.asc()).all()
    results = []
    for d in drivers:
        results.append(
            schemas.DriverOut(
                id=d.id,
                full_name=d.full_name,
                phone=d.phone,
                license_number=d.license_number,
                license_class=d.license_class,
                hazard_training_expiry=d.hazard_training_expiry,
                default_vehicle_id=d.default_vehicle_id,
                default_vehicle_plate=d.default_vehicle.plate_number if d.default_vehicle else None,
                status=d.status,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
        )
    return results


@router.post("/drivers", response_model=schemas.DriverOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(guard("dispatch.drivers"))])
def create_driver(
    payload: schemas.DriverCreate,
    db: Session = Depends(get_db),
):
    driver = models.Driver(
        user_id=payload.user_id,
        full_name=payload.full_name,
        phone=payload.phone,
        license_number=payload.license_number,
        license_class=payload.license_class,
        hazard_training_expiry=payload.hazard_training_expiry,
        default_vehicle_id=payload.default_vehicle_id,
        status=payload.status,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return schemas.DriverOut(
        id=driver.id,
        full_name=driver.full_name,
        phone=driver.phone,
        license_number=driver.license_number,
        license_class=driver.license_class,
        hazard_training_expiry=driver.hazard_training_expiry,
        default_vehicle_id=driver.default_vehicle_id,
        default_vehicle_plate=driver.default_vehicle.plate_number if driver.default_vehicle else None,
        status=driver.status,
        created_at=driver.created_at,
        updated_at=driver.updated_at,
    )
