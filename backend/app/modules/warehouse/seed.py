"""Du lieu mac dinh cho module kho (Warehouse).

Khoi tao 3 kho (48 vi tri), ton kho theo lo thuc te khop voi Warehouse.dc.html,
phieu xuat cho xu ly, phieu nhap va kiem ke mau.
"""
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.warehouse.models import Audit, Dispatch, DispatchItem, Location, Receipt, ReceiptItem, StockItem


def seed_warehouse_data(db: Session) -> None:
    # 1. Locations (3 kho: Kho A, Kho B, Kho C - 48 vi tri)
    if not db.query(Location).first():
        locations_data = []
        # Kho A: Thanh pham (20 vi tri)
        for shelf in range(1, 6):
            for bin_idx in range(1, 5):
                code = f"A-{shelf:02d}-{bin_idx}"
                locations_data.append(Location(
                    warehouse_name="Kho A - Thành phẩm",
                    code=code,
                    zone="Khu A",
                    shelf=f"Kệ {shelf:02d}",
                    bin=f"Tầng {bin_idx}",
                    note="Lưu trữ phụ gia mạ thành phẩm",
                ))

        # Kho B: Nguyen lieu (16 vi tri bao gom ca kho doc)
        for shelf in range(1, 4):
            for bin_idx in range(1, 5):
                code = f"B-{shelf:02d}-{bin_idx}"
                locations_data.append(Location(
                    warehouse_name="Kho B - Nguyên liệu",
                    code=code,
                    zone="Khu B",
                    shelf=f"Kệ {shelf:02d}",
                    bin=f"Tầng {bin_idx}",
                    note="Lưu trữ hóa chất cơ bản, axit/kiềm",
                ))
        # Vi tri dac biet kho doc Kho B
        for bin_idx in range(1, 5):
            locations_data.append(Location(
                warehouse_name="Kho B - Nguyên liệu",
                code=f"B-KĐ-{bin_idx}",
                zone="Khu B độc hại",
                shelf="Kệ KĐ - Kho độc",
                bin=f"Ngăn {bin_idx}",
                note="Lưu trữ chất độc và chất oxy hoá mạnh, có khóa an toàn",
            ))

        # Kho C: Bao bi (12 vi tri)
        for shelf in range(1, 4):
            for bin_idx in range(1, 5):
                code = f"C-{shelf:02d}-{bin_idx}"
                locations_data.append(Location(
                    warehouse_name="Kho C - Bao bì",
                    code=code,
                    zone="Khu C",
                    shelf=f"Kệ {shelf:02d}",
                    bin=f"Tầng {bin_idx}",
                    note="Can nhựa 25L, 30L, phuy 200L, thùng carton",
                ))

        db.add_all(locations_data)
        db.flush()

    # 2. Stock items matching Warehouse.dc.html table
    if not db.query(StockItem).first():
        stock_data = [
            StockItem(
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
                note="Đạt tiêu chuẩn xuất xưởng, đóng can 25kg",
            ),
            StockItem(
                product_code="CRT-650",
                product_name="Phụ gia crom CRT-650",
                category="finished",
                lot_number="L2608-11",
                expiration_date=date(2027, 2, 28),
                location_code="A-04-1",
                quantity=Decimal("96"),
                unit="kg",
                hazard_types="corrosive",
                min_threshold=Decimal("500"),
                max_capacity=Decimal("500"),
                note="Dưới mức an toàn, cần lên kế hoạch pha chế thêm",
            ),
            StockItem(
                product_code="CU-4",
                product_name="Phụ gia mạ đồng",
                category="finished",
                lot_number="L2609-05",
                expiration_date=date(2027, 8, 31),
                location_code="A-03-2",
                quantity=Decimal("310"),
                unit="kg",
                hazard_types="corrosive",
                min_threshold=Decimal("150"),
                max_capacity=Decimal("500"),
                note="Phụ gia tạo bóng đồng acid",
            ),
            StockItem(
                product_code="NL-NaOH",
                product_name="Natri hydroxit",
                category="material",
                lot_number="N2607-01",
                expiration_date=date(2028, 7, 31),
                location_code="B-01-1",
                quantity=Decimal("1200"),
                unit="kg",
                hazard_types="corrosive",
                min_threshold=Decimal("500"),
                max_capacity=Decimal("1600"),
                note="Dạng vảy 99%, bao 25kg có lót PE chống ẩm",
            ),
            StockItem(
                product_code="NL-CrO3",
                product_name="Crom trioxit",
                category="material",
                lot_number="N2605-03",
                expiration_date=date(2027, 5, 31),
                location_code="B-KĐ-1",
                quantity=Decimal("40"),
                unit="kg",
                hazard_types="oxidizing,toxic",
                min_threshold=Decimal("100"),
                max_capacity=Decimal("330"),
                note="Chất oxy hoá mạnh, lưu trữ kho riêng cách ly hữu cơ",
            ),
            StockItem(
                product_code="BB-CAN25",
                product_name="Can nhựa 25 L",
                category="packaging",
                lot_number="—",
                expiration_date=None,
                location_code="C-01-4",
                quantity=Decimal("650"),
                unit="cái",
                hazard_types="",
                min_threshold=Decimal("300"),
                max_capacity=Decimal("1200"),
                note="Can HDPE xanh dương nắp có seal chống tràn",
            ),
        ]
        db.add_all(stock_data)
        db.flush()

    # 3. Dispatches (Phieu xuat cho xu ly matching Warehouse.dc.html)
    if not db.query(Dispatch).first():
        today = date.today()
        d1 = Dispatch(
            dispatch_code="PX-2609-14",
            customer_name="Xi mạ Tân Phú",
            dispatch_date=today,
            status="pending",
            items_summary="NI-534C × 4 can · CU-4 × 2 can",
            receiver_name="Nguyễn Văn Tài",
            note="Khách cần giao trước 15h00 chiều nay",
        )
        d1.items = [
            DispatchItem(product_code="NI-534C", product_name="Phụ gia mạ niken", lot_number="L2609-02", quantity=Decimal("100"), unit="kg", status="pending"),
            DispatchItem(product_code="CU-4", product_name="Phụ gia mạ đồng", lot_number="L2609-05", quantity=Decimal("50"), unit="kg", status="pending"),
        ]

        d2 = Dispatch(
            dispatch_code="PX-2609-13",
            customer_name="Mạ Kẽm Bình Dương",
            dispatch_date=today,
            status="picked",
            items_summary="CRT-650 × 6 can",
            receiver_name="Trần Đình Trọng",
            note="Đã soạn xong để ở khu vực chờ xe",
        )
        d2.items = [
            DispatchItem(product_code="CRT-650", product_name="Phụ gia crom CRT-650", lot_number="L2608-11", quantity=Decimal("150"), unit="kg", status="picked"),
        ]

        d3 = Dispatch(
            dispatch_code="PX-2609-12",
            customer_name="Cơ khí Minh Tâm",
            dispatch_date=today,
            status="loaded",
            items_summary="NI-534C × 2 can",
            receiver_name="Lê Hoàng",
            driver_name="Nguyễn Văn Hùng",
            vehicle_plate="59C-123.45",
            note="Đã bàn giao cho tài xế",
        )
        d3.items = [
            DispatchItem(product_code="NI-534C", product_name="Phụ gia mạ niken", lot_number="L2609-02", quantity=Decimal("50"), unit="kg", status="picked"),
        ]

        db.add_all([d1, d2, d3])
        db.flush()

    # 4. Receipts
    if not db.query(Receipt).first():
        r1 = Receipt(
            receipt_code="PN-2609-01",
            receipt_type="purchase",
            supplier_name="Công ty Hoá chất Á Châu",
            receipt_date=date.today() - timedelta(days=2),
            status="completed",
            note="Nhập hóa chất nguyên liệu đợt cuối tháng",
        )
        r1.items = [
            ReceiptItem(product_code="NL-NaOH", product_name="Natri hydroxit", category="material", lot_number="N2607-01", quantity=Decimal("1000"), unit="kg", location_code="B-01-1"),
            ReceiptItem(product_code="NL-CrO3", product_name="Crom trioxit", category="material", lot_number="N2605-03", quantity=Decimal("200"), unit="kg", location_code="B-KĐ-1"),
        ]
        db.add(r1)
        db.flush()

    # 5. Audits
    if not db.query(Audit).first():
        a1 = Audit(
            audit_code="KK-2609-01",
            warehouse_name="Kho A - Thành phẩm",
            audit_date=date.today() - timedelta(days=3),
            status="completed",
            auditor_name="Phạm Quốc Bảo",
            note="Kiểm kê định kỳ tháng 9 khớp 100% sổ sách",
        )
        db.add(a1)
        db.flush()

    db.commit()
