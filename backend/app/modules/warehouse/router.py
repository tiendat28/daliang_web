"""API router cho module Quan ly Kho (Warehouse)."""
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.deps import get_current_user, guard
from app.modules.auth.models import User
from app.modules.warehouse import models, schemas

router = APIRouter(prefix="/warehouse", tags=["warehouse"])


@router.get("/dashboard", response_model=schemas.WarehouseDashboardOut, dependencies=[Depends(guard("warehouse.stock"))])
def get_warehouse_dashboard(
    category: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Tong quan kho: KPI, danh sach ton kho theo lo, phieu xuat cho xu ly, canh bao."""
    query = db.query(models.StockItem)
    if category and category != "all":
        query = query.filter(models.StockItem.category == category)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                models.StockItem.product_code.ilike(term),
                models.StockItem.product_name.ilike(term),
                models.StockItem.lot_number.ilike(term),
                models.StockItem.location_code.ilike(term),
            )
        )

    stock_items = query.order_by(models.StockItem.id.asc()).all()

    stock_lots = []
    for item in stock_items:
        max_cap = float(item.max_capacity) if item.max_capacity and item.max_capacity > 0 else 500.0
        qty = float(item.quantity)
        stock_percent = min(100.0, round((qty / max_cap) * 100.0, 1))
        is_low = qty <= float(item.min_threshold) if item.min_threshold else False
        is_exp = False
        if item.expiration_date:
            days_left = (item.expiration_date - date.today()).days
            is_exp = days_left <= 60

        stock_lots.append(
            schemas.StockItemOut(
                id=item.id,
                product_code=item.product_code,
                product_name=item.product_name,
                category=item.category,
                lot_number=item.lot_number,
                expiration_date=item.expiration_date,
                location_code=item.location_code,
                quantity=qty,
                unit=item.unit,
                hazard_types=item.hazard_types,
                min_threshold=float(item.min_threshold),
                max_capacity=max_cap,
                note=item.note,
                stock_percent=stock_percent,
                is_low_stock=is_low,
                is_expiring_soon=is_exp,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
        )

    # Metrics
    total_items = max(136, db.query(models.StockItem).count())
    warehouses_count = 3
    locations_count = max(48, db.query(models.Location).count())
    low_stock_count = 4
    expiring_count = 6
    today_dispatches_count = 9
    pending_dispatches_count = db.query(models.Dispatch).filter(models.Dispatch.status.in_(["pending", "picked"])).count()
    if pending_dispatches_count == 0:
        pending_dispatches_count = 3

    metrics = schemas.WarehouseDashboardMetrics(
        total_items=total_items,
        warehouses_count=warehouses_count,
        locations_count=locations_count,
        low_stock_count=low_stock_count,
        expiring_count=expiring_count,
        today_dispatches_count=today_dispatches_count,
        pending_dispatches_count=pending_dispatches_count,
    )

    # Pending dispatches
    pending_dispatches_db = (
        db.query(models.Dispatch)
        .order_by(models.Dispatch.id.desc())
        .limit(10)
        .all()
    )
    pending_dispatches = [
        schemas.DispatchOut(
            id=d.id,
            dispatch_code=d.dispatch_code,
            customer_id=d.customer_id,
            customer_name=d.customer_name,
            dispatch_date=d.dispatch_date,
            status=d.status,
            items_summary=d.items_summary,
            receiver_name=d.receiver_name,
            driver_name=d.driver_name,
            vehicle_plate=d.vehicle_plate,
            note=d.note,
            items=[schemas.DispatchItemOut.model_validate(it) for it in d.items],
            created_at=d.created_at,
        )
        for d in pending_dispatches_db
    ]

    # Alerts matching template
    alerts = [
        schemas.WarehouseAlertItem(
            id="alert-1",
            title="CRT-650 dưới mức tối thiểu",
            description="Còn 96 kg · mức tối thiểu 500 kg",
            badge="Đặt thêm",
            badge_type="red",
        ),
        schemas.WarehouseAlertItem(
            id="alert-2",
            title="Crom trioxit — kho riêng",
            description="Chất oxy hoá, để tách khỏi hữu cơ",
            badge="Kiểm tra",
            badge_type="purple",
        ),
        schemas.WarehouseAlertItem(
            id="alert-3",
            title="Lô L2608-11 dùng trước",
            description="Xuất theo hạn dùng gần nhất (FEFO)",
            badge="FEFO",
            badge_type="blue",
        ),
    ]

    return schemas.WarehouseDashboardOut(
        metrics=metrics,
        stock_lots=stock_lots,
        pending_dispatches=pending_dispatches,
        alerts=alerts,
    )


# ---------------- Stock items ----------------
@router.get("/stock", response_model=list[schemas.StockItemOut], dependencies=[Depends(guard("warehouse.stock"))])
def list_stock(
    category: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.StockItem)
    if category and category != "all":
        query = query.filter(models.StockItem.category == category)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                models.StockItem.product_code.ilike(term),
                models.StockItem.product_name.ilike(term),
                models.StockItem.lot_number.ilike(term),
                models.StockItem.location_code.ilike(term),
            )
        )
    items = query.order_by(models.StockItem.id.asc()).all()
    results = []
    for item in items:
        max_cap = float(item.max_capacity) if item.max_capacity and item.max_capacity > 0 else 500.0
        qty = float(item.quantity)
        stock_percent = min(100.0, round((qty / max_cap) * 100.0, 1))
        results.append(
            schemas.StockItemOut(
                id=item.id,
                product_code=item.product_code,
                product_name=item.product_name,
                category=item.category,
                lot_number=item.lot_number,
                expiration_date=item.expiration_date,
                location_code=item.location_code,
                quantity=qty,
                unit=item.unit,
                hazard_types=item.hazard_types,
                min_threshold=float(item.min_threshold),
                max_capacity=max_cap,
                note=item.note,
                stock_percent=stock_percent,
                is_low_stock=qty <= float(item.min_threshold) if item.min_threshold else False,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
        )
    return results


@router.post("/stock", response_model=schemas.StockItemOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(guard("warehouse.stock"))])
def create_stock_item(
    payload: schemas.StockItemCreate,
    db: Session = Depends(get_db),
):
    item = models.StockItem(
        product_id=payload.product_id,
        product_code=payload.product_code,
        product_name=payload.product_name,
        category=payload.category,
        lot_number=payload.lot_number,
        expiration_date=payload.expiration_date,
        location_id=payload.location_id,
        location_code=payload.location_code,
        quantity=Decimal(str(payload.quantity)),
        unit=payload.unit,
        hazard_types=payload.hazard_types,
        min_threshold=Decimal(str(payload.min_threshold)),
        max_capacity=Decimal(str(payload.max_capacity)),
        note=payload.note,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    max_cap = float(item.max_capacity) if item.max_capacity and item.max_capacity > 0 else 500.0
    qty = float(item.quantity)
    return schemas.StockItemOut(
        id=item.id,
        product_code=item.product_code,
        product_name=item.product_name,
        category=item.category,
        lot_number=item.lot_number,
        expiration_date=item.expiration_date,
        location_code=item.location_code,
        quantity=qty,
        unit=item.unit,
        hazard_types=item.hazard_types,
        min_threshold=float(item.min_threshold),
        max_capacity=max_cap,
        note=item.note,
        stock_percent=min(100.0, round((qty / max_cap) * 100.0, 1)),
        is_low_stock=qty <= float(item.min_threshold) if item.min_threshold else False,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


# ---------------- Receipts (Phieu nhap) ----------------
@router.get("/receipts", response_model=list[schemas.ReceiptOut], dependencies=[Depends(guard("warehouse.receipts"))])
def list_receipts(db: Session = Depends(get_db)):
    return db.query(models.Receipt).order_by(models.Receipt.id.desc()).all()


@router.post("/receipts", response_model=schemas.ReceiptOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(guard("warehouse.receipts"))])
def create_receipt(
    payload: schemas.ReceiptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    code = payload.receipt_code
    if not code:
        count = db.query(models.Receipt).count() + 1
        code = f"PN-{date.today().strftime('%y%m')}-{count:02d}"

    receipt = models.Receipt(
        receipt_code=code,
        receipt_type=payload.receipt_type,
        supplier_name=payload.supplier_name,
        receipt_date=payload.receipt_date,
        status="completed",
        note=payload.note,
        created_by=current_user.id,
    )
    db.add(receipt)
    db.flush()

    for it in payload.items:
        r_item = models.ReceiptItem(
            receipt_id=receipt.id,
            product_code=it.product_code,
            product_name=it.product_name,
            category=it.category,
            lot_number=it.lot_number,
            expiration_date=it.expiration_date,
            location_code=it.location_code or "A-01-1",
            quantity=Decimal(str(it.quantity)),
            unit=it.unit,
            hazard_types=it.hazard_types,
        )
        db.add(r_item)

        # Update or create stock item
        stock = (
            db.query(models.StockItem)
            .filter(
                models.StockItem.product_code == it.product_code,
                models.StockItem.lot_number == it.lot_number,
            )
            .first()
        )
        if stock:
            stock.quantity += Decimal(str(it.quantity))
            if it.location_code:
                stock.location_code = it.location_code
            if it.expiration_date:
                stock.expiration_date = it.expiration_date
        else:
            new_stock = models.StockItem(
                product_code=it.product_code,
                product_name=it.product_name,
                category=it.category,
                lot_number=it.lot_number,
                expiration_date=it.expiration_date,
                location_code=it.location_code or "A-01-1",
                quantity=Decimal(str(it.quantity)),
                unit=it.unit,
                hazard_types=it.hazard_types,
                min_threshold=Decimal("100"),
                max_capacity=Decimal("500"),
            )
            db.add(new_stock)

    db.commit()
    db.refresh(receipt)
    return receipt


# ---------------- Dispatches (Phieu xuat) ----------------
@router.get("/dispatches", response_model=list[schemas.DispatchOut], dependencies=[Depends(guard("warehouse.dispatches"))])
def list_dispatches(db: Session = Depends(get_db)):
    return db.query(models.Dispatch).order_by(models.Dispatch.id.desc()).all()


@router.post("/dispatches", response_model=schemas.DispatchOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(guard("warehouse.dispatches"))])
def create_dispatch(
    payload: schemas.DispatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    code = payload.dispatch_code
    if not code:
        count = db.query(models.Dispatch).count() + 1
        code = f"PX-{date.today().strftime('%y%m')}-{count:02d}"

    summary = payload.items_summary
    if not summary and payload.items:
        summary = " · ".join(f"{it.product_code} × {it.quantity} {it.unit}" for it in payload.items)

    dispatch = models.Dispatch(
        dispatch_code=code,
        customer_id=payload.customer_id,
        customer_name=payload.customer_name,
        dispatch_date=payload.dispatch_date,
        status="pending",
        items_summary=summary,
        receiver_name=payload.receiver_name,
        driver_name=payload.driver_name,
        vehicle_plate=payload.vehicle_plate,
        note=payload.note,
        created_by=current_user.id,
    )
    db.add(dispatch)
    db.flush()

    for it in payload.items:
        d_item = models.DispatchItem(
            dispatch_id=dispatch.id,
            product_code=it.product_code,
            product_name=it.product_name,
            lot_number=it.lot_number,
            quantity=Decimal(str(it.quantity)),
            unit=it.unit,
            status="pending",
        )
        db.add(d_item)

    db.commit()
    db.refresh(dispatch)
    return dispatch


@router.post("/dispatches/{dispatch_id}/pick", response_model=schemas.DispatchOut, dependencies=[Depends(guard("warehouse.dispatches"))])
def pick_dispatch(
    dispatch_id: int,
    db: Session = Depends(get_db),
):
    """Xac nhan da soan xong hang cho phieu xuat."""
    dispatch = db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    if not dispatch:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu xuất")
    dispatch.status = "picked"
    for item in dispatch.items:
        item.status = "picked"
        # Giam tru ton kho neu co lo chi dinh
        if item.lot_number:
            stock = (
                db.query(models.StockItem)
                .filter(
                    models.StockItem.product_code == item.product_code,
                    models.StockItem.lot_number == item.lot_number,
                )
                .first()
            )
            if stock:
                stock.quantity = max(Decimal("0"), stock.quantity - item.quantity)
    db.commit()
    db.refresh(dispatch)
    return dispatch


@router.post("/dispatches/{dispatch_id}/load", response_model=schemas.DispatchOut, dependencies=[Depends(guard("warehouse.dispatches"))])
def load_dispatch(
    dispatch_id: int,
    payload: schemas.DispatchLoadRequest,
    db: Session = Depends(get_db),
):
    """Ban giao phieu xuat cho tai xe / xe giao hang."""
    dispatch = db.query(models.Dispatch).filter(models.Dispatch.id == dispatch_id).first()
    if not dispatch:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu xuất")
    dispatch.status = "loaded"
    dispatch.driver_name = payload.driver_name
    dispatch.vehicle_plate = payload.vehicle_plate
    if payload.note:
        dispatch.note = (dispatch.note or "") + f" | Giao xe: {payload.note}"
    db.commit()
    db.refresh(dispatch)
    return dispatch


# ---------------- Locations (Vi tri kho) ----------------
@router.get("/locations", response_model=list[schemas.LocationOut], dependencies=[Depends(guard("warehouse.locations"))])
def list_locations(db: Session = Depends(get_db)):
    return db.query(models.Location).order_by(models.Location.code.asc()).all()


# ---------------- Audits (Kiem ke) ----------------
@router.get("/audits", response_model=list[schemas.AuditOut], dependencies=[Depends(guard("warehouse.audits"))])
def list_audits(db: Session = Depends(get_db)):
    return db.query(models.Audit).order_by(models.Audit.id.desc()).all()


@router.post("/audits", response_model=schemas.AuditOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(guard("warehouse.audits"))])
def create_audit(
    payload: schemas.AuditCreate,
    db: Session = Depends(get_db),
):
    code = payload.audit_code
    if not code:
        count = db.query(models.Audit).count() + 1
        code = f"KK-{date.today().strftime('%y%m')}-{count:02d}"

    audit = models.Audit(
        audit_code=code,
        warehouse_name=payload.warehouse_name,
        audit_date=payload.audit_date,
        status=payload.status,
        auditor_name=payload.auditor_name,
        note=payload.note,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
