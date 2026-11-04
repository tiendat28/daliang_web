"""Smoke test cho module Kho (Warehouse)."""
from datetime import date, timedelta
from decimal import Decimal
import pytest

from app.modules.warehouse import models, schemas


def test_warehouse_models_and_schemas_in_memory():
    # 1. Test StockItem schema
    item = schemas.StockItemOut(
        id=1,
        product_code="NI-534C",
        product_name="Phụ gia mạ niken",
        category="finished",
        lot_number="L2609-02",
        expiration_date=date(2027, 9, 30),
        location_code="A-02-3",
        quantity=420.0,
        unit="kg",
        hazard_types="toxic",
        min_threshold=200.0,
        max_capacity=500.0,
        stock_percent=84.0,
        is_low_stock=False,
        is_expiring_soon=False,
        created_at=date.today(),
        updated_at=date.today(),
    )
    assert item.stock_percent == 84.0
    assert item.category == "finished"
    assert item.location_code == "A-02-3"

    # 2. Test Low stock item
    low_item = schemas.StockItemOut(
        id=2,
        product_code="CRT-650",
        product_name="Phụ gia crom CRT-650",
        category="finished",
        lot_number="L2608-11",
        expiration_date=date(2027, 2, 28),
        location_code="A-04-1",
        quantity=96.0,
        unit="kg",
        hazard_types="corrosive",
        min_threshold=500.0,
        max_capacity=500.0,
        stock_percent=19.2,
        is_low_stock=True,
        is_expiring_soon=False,
        created_at=date.today(),
        updated_at=date.today(),
    )
    assert low_item.is_low_stock is True
    assert low_item.quantity == 96.0

    # 3. Test Dashboard Out schema
    dashboard = schemas.WarehouseDashboardOut(
        metrics=schemas.WarehouseDashboardMetrics(
            total_items=136,
            warehouses_count=3,
            locations_count=48,
            low_stock_count=4,
            expiring_count=6,
            today_dispatches_count=9,
            pending_dispatches_count=3,
        ),
        stock_lots=[item, low_item],
        pending_dispatches=[],
        alerts=[
            schemas.WarehouseAlertItem(
                title="CRT-650 dưới mức tối thiểu",
                description="Còn 96 kg · mức tối thiểu 500 kg",
                badge="Đặt thêm",
                badge_type="red",
            )
        ],
    )
    assert dashboard.metrics.total_items == 136
    assert dashboard.metrics.warehouses_count == 3
    assert len(dashboard.stock_lots) == 2
    assert len(dashboard.alerts) == 1


def test_warehouse_db_flow(db_session):
    # Tao location
    loc = models.Location(
        warehouse_name="Kho A - Thành phẩm",
        code="A-02-3",
        zone="Khu A",
        shelf="Kệ 02",
        bin="Tầng 3",
    )
    db_session.add(loc)
    db_session.flush()
    assert loc.id is not None

    # Tao stock item
    stock = models.StockItem(
        product_code="NI-534C",
        product_name="Phụ gia mạ niken",
        category="finished",
        lot_number="L2609-02",
        expiration_date=date(2027, 9, 30),
        location_code="A-02-3",
        quantity=Decimal("420"),
        unit="kg",
        hazard_types="toxic",
        min_threshold=Decimal("200"),
        max_capacity=Decimal("500"),
    )
    db_session.add(stock)
    db_session.flush()
    assert stock.quantity == 420

    # Tao dispatch (phieu xuat)
    disp = models.Dispatch(
        dispatch_code="PX-2609-14",
        customer_name="Xi mạ Tân Phú",
        dispatch_date=date.today(),
        status="pending",
        items_summary="NI-534C × 4 can",
    )
    disp.items = [
        models.DispatchItem(
            product_code="NI-534C",
            product_name="Phụ gia mạ niken",
            lot_number="L2609-02",
            quantity=Decimal("100"),
            unit="kg",
            status="pending",
        )
    ]
    db_session.add(disp)
    db_session.flush()

    # Soan hang
    disp.status = "picked"
    for it in disp.items:
        it.status = "picked"
        stock.quantity -= it.quantity

    db_session.flush()
    assert stock.quantity == 320
    assert disp.status == "picked"

    # Giao xe
    disp.status = "loaded"
    disp.driver_name = "Nguyễn Văn Hùng"
    disp.vehicle_plate = "59C-123.45"
    db_session.flush()

    assert disp.status == "loaded"
    assert disp.driver_name == "Nguyễn Văn Hùng"
