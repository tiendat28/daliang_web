"""Du lieu mau cho module "Luu trinh test mau".

Chay bang tay:  docker compose exec backend python -m app.core.seed

Idempotent: doi chieu theo ma / ten, co roi thi bo qua, khong ghi de du lieu
dang co. Rieng letterhead (company_profile) duoc tao tu dong luc backend khoi
dong vi khong co no thi khong in duoc phieu.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app import models
from app.core.database import SessionLocal

COMPANY_PROFILE = {
    "logo_path": "img/logo-dlvc.png",
    "name_zh": "越南大亮化工有限公司",
    "name_en": "DALIANG CHEMICAL VIETNAM CO.,LTD",
    "address_zh": "越南平陽省新淵縣帝國社帝國工業區 D2 路",
    "phone": "0650-3651005~09",
    "fax": "0650-3651010",
}

SEED_CUSTOMER = "Nhà máy Z-113"

# (ma, ten) - san pham cong ty duoc nhac trong phieu mau
SEED_PRODUCTS = [
    ("NCZ-48A", "NCZ-48A"),
    ("NCZ-48B", "NCZ-48B"),
    ("NCZ-48C", "NCZ-48C"),
    ("NCZ-48R", "NCZ-48R"),
    ("CHB-60", "CHB-60"),
    ("CR-3GD", "CR-3GD"),
]

SEED_LAB_CHEMICALS = [("HNO3", "Axit nitric")]


def _step(position, operation, **kwargs):
    """1 buoc; concentrations/chemicals la list tuple de goi cho gon o duoi."""
    return {"position": position, "operation": operation, **kwargs}


# Dung 100% theo mau-goc.png - day cung la ky vong cua ban in ra.
LT_2026_001_STEPS = [
    _step(1, "Tiền xử lí"),
    _step(
        2, "Mạ kẽm kiềm",
        time=(50, None, "min"), temp=("range", 20, 30),
        concentrations=[("Zn^2+", 8, 16, "g/l"), ("NaOH", 110, 160, "g/l")],
        products=["NCZ-48A", "NCZ-48B", "NCZ-48C", "NCZ-48R"],
    ),
    _step(3, "Rửa nước", time=(2, 3, "min"), temp=("ambient", None, None)),
    _step(
        4, "Tẩy sáng",
        time=(3, 5, "sec"),
        concentrations=[(None, 0.5, None, "%")],
        lab_chemicals=[("HNO3", "HNO_3")],
    ),
    _step(5, "Rửa nước", time=(1, 2, "min"), temp=("ambient", None, None)),
    _step(
        6, "Thụ động",
        time=(5, 15, "sec"), temp=("range", 20, 30), ph=(1.3, 1.8),
        concentrations=[(None, 10, None, "%")],
        products=["CHB-60"],
    ),
    _step(7, "Rửa nước x2", time=(1, None, "min"), temp=("ambient", None, None)),
    _step(
        8, "Nhuộm màu",
        time=(5, 10, "min"), temp=("range", 60, 70),
        concentrations=[(None, 20, None, "%")],
        products=["CR-3GD"],
    ),
    _step(9, "Rửa nước x2", time=(1, 2, "min"), temp=("ambient", None, None)),
    _step(10, "Sấy", time=(10, 30, "min"), temp=("range", 80, 100)),
]


TEMPLATE_NAME = "Mạ kẽm kiềm – thụ động – nhuộm màu"

# 16 buoc - dung de thu che do hang thap (tren 12 buoc) van vua 1 trang A4
LT_2026_016_STEPS = [
    _step(1, "Tẩy dầu điện phân", time=(3, 5, "min"), temp=("range", 50, 60),
          concentrations=[(None, 50, 80, "g/l")]),
    _step(2, "Rửa nước", time=(1, 2, "min"), temp=("ambient", None, None)),
    _step(3, "Tẩy gỉ", time=(5, 10, "min"), temp=("ambient", None, None),
          concentrations=[(None, 10, 15, "%")], lab_chemicals=[("HNO3", "HNO_3")]),
    _step(4, "Rửa nước x2", time=(1, None, "min"), temp=("ambient", None, None)),
    _step(5, "Hoạt hóa", time=(30, 60, "sec"), temp=("ambient", None, None),
          concentrations=[(None, 3, 5, "%")]),
    _step(6, "Rửa nước", time=(1, None, "min"), temp=("ambient", None, None)),
    _step(7, "Mạ kẽm kiềm", time=(40, 60, "min"), temp=("range", 20, 30),
          concentrations=[("Zn^2+", 8, 16, "g/l"), ("NaOH", 110, 160, "g/l")],
          products=["NCZ-48A", "NCZ-48B", "NCZ-48C"]),
    _step(8, "Rửa nước x2", time=(2, 3, "min"), temp=("ambient", None, None)),
    _step(9, "Tẩy sáng", time=(3, 5, "sec"), concentrations=[(None, 0.5, None, "%")],
          lab_chemicals=[("HNO3", "HNO_3")]),
    _step(10, "Rửa nước", time=(1, 2, "min"), temp=("ambient", None, None)),
    _step(11, "Thụ động", time=(20, 40, "sec"), temp=("range", 25, 30), ph=(1.6, 2.0),
          concentrations=[(None, 8, 12, "%")], products=["CHB-60"]),
    _step(12, "Rửa nước", time=(1, None, "min"), temp=("ambient", None, None)),
    _step(13, "Nhuộm màu", time=(5, 10, "min"), temp=("range", 60, 70),
          concentrations=[(None, 20, None, "%")], products=["CR-3GD"]),
    _step(14, "Rửa nước x2", time=(1, 2, "min"), temp=("ambient", None, None)),
    _step(15, "Phủ bảo vệ", time=(30, 60, "sec"), temp=("range", 30, 40),
          concentrations=[(None, 5, 8, "%")]),
    _step(16, "Sấy", time=(15, 30, "min"), temp=("range", 80, 100)),
]

LT_2026_002_STEPS = [
    _step(1, "Tẩy dầu", time=(5, None, "min"), temp=("range", 45, 55),
          concentrations=[(None, 40, 60, "g/l")]),
    _step(2, "Rửa nước", time=(1, 2, "min"), temp=("ambient", None, None)),
    _step(3, "Mạ kẽm acid", time=(30, 45, "min"), temp=("range", 25, 35),
          ph=(4.8, 5.4), concentrations=[("Zn^2+", 30, 45, "g/l")],
          products=["NCZ-48A", "NCZ-48R"]),
    _step(4, "Rửa nước x2", time=(1, 2, "min"), temp=("ambient", None, None)),
    _step(5, "Thụ động", time=(10, 20, "sec"), ph=(1.3, 1.8),
          concentrations=[(None, 10, None, "%")], products=["CHB-60"]),
    _step(6, "Sấy", time=(10, 20, "min"), temp=("range", 70, 90)),
]

LT_2025_014_STEPS = [
    _step(1, "Tiền xử lí"),
    _step(2, "Mạ kẽm kiềm", time=(45, None, "min"), temp=("range", 20, 28),
          concentrations=[("Zn^2+", 10, 14, "g/l")], products=["NCZ-48A", "NCZ-48B"]),
    _step(3, "Rửa nước", time=(2, None, "min"), temp=("ambient", None, None)),
    _step(4, "Thụ động", time=(15, None, "sec"), ph=(1.5, 1.9),
          concentrations=[(None, 10, None, "%")], products=["CHB-60"]),
    _step(5, "Sấy", time=(20, None, "min"), temp=("range", 80, 90)),
]

# (ma, ten khach, cac truong cua luu trinh, bo buoc)
DEMO_PROCESSES = [
    (
        "LT-2026-002", "Công ty TNHH Cơ khí Tiến Đạt",
        {
            "requirement": "lớp mạ sáng bóng, chịu muối phun 72 giờ",
            "sample_quantity": 4,
            "test_month": date(2026, 9, 1),
            "prepared_by": "Vũ Thị Oanh",
            "status": models.TestProcessStatus.in_progress.value,
            "internal_note": "Khách đang chờ kết quả phun muối, chưa chốt giá.",
        },
        LT_2026_002_STEPS,
    ),
    (
        "LT-2026-003", "Nhà máy Z-113",
        {
            "requirement": "quy trình đầy đủ cho chi tiết ren, 16 bước",
            "sample_quantity": 6,
            "test_month": date(2026, 10, 1),
            "prepared_by": "Nguyễn Văn Hùng",
            "status": models.TestProcessStatus.draft.value,
        },
        LT_2026_016_STEPS,
    ),
    (
        "LT-2025-014", "Công ty CP Mạ kẽm Hoàng Long",
        {
            "requirement": "mạ kẽm trắng xanh cho bu lông M8",
            "sample_quantity": 3,
            "test_month": date(2025, 11, 1),
            "prepared_by": "Vũ Thị Oanh",
            "status": models.TestProcessStatus.cancelled.value,
            "internal_note": "Khách đổi sang nhà cung cấp khác.",
        },
        LT_2025_014_STEPS,
    ),
]


def seed_company_profile(engine: Engine) -> None:
    """Tao dong letterhead neu bang con rong. Goi luc backend khoi dong."""
    with Session(engine) as db:
        if db.query(models.CompanyProfile).first():
            return
        db.add(models.CompanyProfile(**COMPANY_PROFILE))
        db.commit()


def _ensure_customer(db: Session, name: str) -> models.Customer:
    customer = db.query(models.Customer).filter_by(name=name).first()
    if not customer:
        customer = models.Customer(name=name)
        db.add(customer)
        db.flush()
    return customer


def _ensure_products(db: Session) -> dict[str, models.CompanyProduct]:
    result = {}
    for code, name in SEED_PRODUCTS:
        product = db.query(models.CompanyProduct).filter_by(code=code).first()
        if not product:
            product = models.CompanyProduct(code=code, name=name)
            db.add(product)
            db.flush()
        result[code] = product
    return result


def _ensure_lab_chemicals(db: Session) -> dict[str, models.LabChemical]:
    result = {}
    for code, name in SEED_LAB_CHEMICALS:
        chemical = db.query(models.LabChemical).filter_by(code=code).first()
        if not chemical:
            chemical = models.LabChemical(code=code, name=name)
            db.add(chemical)
            db.flush()
        result[code] = chemical
    return result


def _add_steps(db: Session, process: models.TestProcess, steps_data, products, lab_chemicals):
    for data in steps_data:
        time_min, time_max, time_unit = data.get("time", (None, None, None))
        temp_mode, temp_min, temp_max = data.get("temp", ("none", None, None))
        ph_min, ph_max = data.get("ph", (None, None))

        step = models.TestProcessStep(
            process_id=process.id,
            position=data["position"],
            operation=data["operation"],
            time_min=time_min, time_max=time_max, time_unit=time_unit,
            temp_mode=temp_mode, temp_min=temp_min, temp_max=temp_max,
            ph_min=ph_min, ph_max=ph_max,
        )
        db.add(step)
        db.flush()

        for index, (component, value_min, value_max, unit) in enumerate(data.get("concentrations", []), start=1):
            db.add(models.TestProcessStepConcentration(
                step_id=step.id, position=index, component=component,
                value_min=value_min, value_max=value_max, unit=unit,
            ))

        position = 0
        for code in data.get("products", []):
            position += 1
            db.add(models.TestProcessStepChemical(
                step_id=step.id, position=position,
                product_id=products[code].id, display_name=code,
            ))
        for code, display_name in data.get("lab_chemicals", []):
            position += 1
            db.add(models.TestProcessStepChemical(
                step_id=step.id, position=position,
                lab_chemical_id=lab_chemicals[code].id, display_name=display_name,
            ))


def _create_process(db, code, customer, steps_data, products, lab_chemicals, **fields):
    """Tao luu trinh neu ma do chua co. Da co thi giu nguyen, khong ghi de."""
    if db.query(models.TestProcess).filter_by(code=code).first():
        return None

    process = models.TestProcess(
        code=code,
        customer_id=customer.id,
        customer_name=customer.name,
        **fields,
    )
    db.add(process)
    db.flush()
    _add_steps(db, process, steps_data, products, lab_chemicals)
    return process


def _steps_as_json(steps_data, products, lab_chemicals):
    """Doi bo buoc sang dang jsonb cua process_templates - cung cau truc voi mang steps cua API."""
    rows = []
    for data in steps_data:
        time_min, time_max, time_unit = data.get("time", (None, None, None))
        temp_mode, temp_min, temp_max = data.get("temp", ("none", None, None))
        ph_min, ph_max = data.get("ph", (None, None))
        chemicals = [
            {"product_id": products[code].id, "lab_chemical_id": None, "display_name": code}
            for code in data.get("products", [])
        ] + [
            {"product_id": None, "lab_chemical_id": lab_chemicals[code].id, "display_name": name}
            for code, name in data.get("lab_chemicals", [])
        ]
        rows.append({
            "operation": data["operation"],
            "time_min": time_min, "time_max": time_max, "time_unit": time_unit,
            "temp_mode": temp_mode, "temp_min": temp_min, "temp_max": temp_max,
            "ph_min": ph_min, "ph_max": ph_max,
            "time_text": None, "temp_text": None, "ph_text": None, "note": None,
            "concentrations": [
                {"component": component, "value_min": value_min, "value_max": value_max,
                 "unit": unit, "text_override": None}
                for component, value_min, value_max, unit in data.get("concentrations", [])
            ],
            "chemicals": chemicals,
        })
    return rows


def seed_test_processes(db: Session) -> None:
    z113 = _ensure_customer(db, SEED_CUSTOMER)
    products = _ensure_products(db)
    lab_chemicals = _ensure_lab_chemicals(db)

    created = []
    if _create_process(
        db, "LT-2026-001", z113, LT_2026_001_STEPS, products, lab_chemicals,
        requirement="sản phẩm sau xử lý có màu xanh than-xanh xám",
        sample_quantity=2,
        test_month=date(2026, 8, 1),
        prepared_by="Vũ Thị Oanh",
        status=models.TestProcessStatus.completed.value,
    ):
        created.append("LT-2026-001")

    for code, customer_name, fields, steps_data in DEMO_PROCESSES:
        customer = _ensure_customer(db, customer_name)
        if _create_process(db, code, customer, steps_data, products, lab_chemicals, **fields):
            created.append(code)

    if not db.query(models.ProcessTemplate).filter_by(name=TEMPLATE_NAME).first():
        db.add(models.ProcessTemplate(
            name=TEMPLATE_NAME,
            description="Bộ bước chuẩn cho hàng mạ kẽm kiềm, lấy từ LT-2026-001.",
            steps=_steps_as_json(LT_2026_001_STEPS, products, lab_chemicals),
        ))
        created.append(f"quy trinh chuan \"{TEMPLATE_NAME}\"")

    db.commit()
    print("Da tao: " + (", ".join(created) if created else "khong co gi moi, du lieu mau da day du."))


def main() -> None:
    with SessionLocal() as db:
        seed_test_processes(db)


if __name__ == "__main__":
    main()
