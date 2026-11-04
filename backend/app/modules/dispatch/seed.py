"""Du lieu mac dinh cho module dieu phoi xe (Dispatch).

Khoi tao doi xe, danh sach 5 tai xe va 6 chuyen giao hang khop 100% Dispatch.dc.html.
"""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.dispatch.models import DeliveryTrip, Driver, Vehicle


def seed_dispatch_data(db: Session) -> None:
    # 1. Vehicles
    if not db.query(Vehicle).first():
        v1 = Vehicle(
            plate_number="51C-892.14",
            vehicle_type="Xe tải 1.5 tấn",
            max_payload_kg=Decimal("1500"),
            hazard_permit_expiry=date(2026, 10, 20),
            status="active",
            notes="Xe chuyên dụng chở hóa chất xi mạ, có sàn chống tràn",
        )
        v2 = Vehicle(
            plate_number="51D-452.19",
            vehicle_type="Xe bán tải 1 tấn",
            max_payload_kg=Decimal("1000"),
            hazard_permit_expiry=date(2027, 3, 15),
            status="active",
            notes="Xe chở mẫu và các đơn hàng nhỏ nội thành",
        )
        v3 = Vehicle(
            plate_number="60C-338.90",
            vehicle_type="Xe tải 2.5 tấn",
            max_payload_kg=Decimal("2500"),
            hazard_permit_expiry=date(2027, 6, 30),
            status="active",
            notes="Xe tuyến Bình Dương, Đồng Nai, Long An",
        )
        v4 = Vehicle(
            plate_number="51C-714.28",
            vehicle_type="Xe tải 1.5 tấn",
            max_payload_kg=Decimal("1500"),
            hazard_permit_expiry=date(2027, 1, 20),
            status="active",
            notes="Xe dự phòng, kiểm định đạt chuẩn",
        )
        db.add_all([v1, v2, v3, v4])
        db.flush()

    v_map = {v.plate_number: v.id for v in db.query(Vehicle).all()}

    # 2. Drivers (5 tai xe matching template)
    if not db.query(Driver).first():
        drivers_data = [
            Driver(
                full_name="Đỗ Thành Long",
                phone="0908 123 456",
                license_number="GPLX-791024",
                license_class="C",
                hazard_training_expiry=date(2026, 10, 20),
                default_vehicle_id=v_map.get("51C-892.14"),
                status="running",  # Đang chạy
            ),
            Driver(
                full_name="Mai Huy",
                phone="0913 234 567",
                license_number="GPLX-852109",
                license_class="C",
                hazard_training_expiry=date(2027, 3, 15),
                default_vehicle_id=v_map.get("51D-452.19"),
                status="running",  # Đang chạy
            ),
            Driver(
                full_name="Trịnh Khoa",
                phone="0982 345 678",
                license_number="GPLX-910432",
                license_class="D",
                hazard_training_expiry=date(2027, 6, 30),
                default_vehicle_id=v_map.get("60C-338.90"),
                status="issue",  # Sự cố
            ),
            Driver(
                full_name="Phan Lực",
                phone="0975 456 789",
                license_number="GPLX-639108",
                license_class="C",
                hazard_training_expiry=date(2027, 1, 20),
                default_vehicle_id=v_map.get("51C-714.28"),
                status="ready",  # Sẵn sàng
            ),
            Driver(
                full_name="Võ Sơn",
                phone="0938 567 890",
                license_number="GPLX-518290",
                license_class="C",
                hazard_training_expiry=None,
                default_vehicle_id=None,
                status="off",  # Nghỉ
            ),
        ]
        db.add_all(drivers_data)
        db.flush()

    d_map = {d.full_name: d.id for d in db.query(Driver).all()}

    # 3. Delivery Trips (6 chuyen giao matching 4 cot Kanban Dispatch.dc.html)
    if not db.query(DeliveryTrip).first():
        today = date.today()
        trips = [
            # Cột 1: Chờ phân công (2 chuyến)
            DeliveryTrip(
                trip_code="CG-2609-14",
                dispatch_code="PX-2609-14",
                customer_name="Xi mạ Tân Phú",
                customer_address="Lô C2-3, Đường số 7, KCN Tân Bình, P. Tây Thạnh, Q. Tân Phú, TP.HCM",
                items_summary="4 can NI-534C · 2 can CU-4",
                is_hazardous=True,
                status="unassigned",
                trip_date=today,
            ),
            DeliveryTrip(
                trip_code="CG-2609-15",
                dispatch_code="PX-2609-15",
                customer_name="Phụ tùng Hưng Thịnh",
                customer_address="124/8 Quốc lộ 1A, Xã Tân Kiên, Huyện Bình Chánh, TP.HCM",
                items_summary="8 can bao bì rỗng",
                is_hazardous=False,
                status="unassigned",
                trip_date=today,
            ),
            # Cột 2: Đang giao (2 chuyến)
            DeliveryTrip(
                trip_code="CG-2609-13",
                dispatch_code="PX-2609-13",
                customer_name="Mạ Kẽm Bình Dương",
                customer_address="Đường số 4, KCN Sóng Thần 1, TP. Dĩ An, Tỉnh Bình Dương",
                items_summary="6 can CRT-650",
                is_hazardous=True,
                driver_id=d_map.get("Đỗ Thành Long"),
                vehicle_id=v_map.get("51C-892.14"),
                status="delivering",
                estimated_time="Dự kiến 10:40",
                trip_date=today,
            ),
            DeliveryTrip(
                trip_code="CG-2609-11",
                dispatch_code="PX-2609-11",
                customer_name="Kim khí Đông Á",
                customer_address="Đường 3A, KCN Biên Hòa 2, TP. Biên Hòa, Tỉnh Đồng Nai",
                items_summary="3 can NI-534C",
                is_hazardous=True,
                driver_id=d_map.get("Mai Huy"),
                vehicle_id=v_map.get("51D-452.19"),
                status="delivering",
                estimated_time="Dự kiến 11:15",
                trip_date=today,
            ),
            # Cột 3: Đã giao (1 chuyến)
            DeliveryTrip(
                trip_code="CG-2609-12",
                dispatch_code="PX-2609-12",
                customer_name="Cơ khí Minh Tâm",
                customer_address="45/2 Tô Ký, P. Tân Chánh Hiệp, Quận 12, TP.HCM",
                items_summary="2 can NI-534C",
                is_hazardous=True,
                driver_id=d_map.get("Mai Huy"),
                vehicle_id=v_map.get("51D-452.19"),
                status="delivered",
                delivered_at=datetime.combine(today, datetime.min.time()).replace(hour=8, minute=52),
                proof_image_url="/static/delivery_proofs/PX-2609-12_signed.jpg",
                issue_note="Giao 08:52 · có ảnh biên nhận",
                trip_date=today,
            ),
            # Cột 4: Sự cố (1 chuyến)
            DeliveryTrip(
                trip_code="CG-2609-09",
                dispatch_code="PX-2609-09",
                customer_name="Xi mạ Phú Thọ",
                customer_address="KCN Đức Hòa 1, Xã Đức Hòa Đông, Huyện Đức Hòa, Tỉnh Long An",
                items_summary="5 can CU-4",
                is_hazardous=True,
                driver_id=d_map.get("Trịnh Khoa"),
                vehicle_id=v_map.get("60C-338.90"),
                status="issue",
                issue_note="Khách vắng — hẹn lại",
                trip_date=today,
            ),
        ]
        db.add_all(trips)
        db.flush()

    db.commit()
