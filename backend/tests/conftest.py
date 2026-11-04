"""Tien ich dung chung cho test cua module "Luu trinh test mau".

Test chay tren mot DB rieng (`<db>_test`) chu khong dung DB that: fixture co
xoa sach bang giua cac test, dung nham DB la mat du lieu dang dung.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------- Du lieu dung cho test formatter / to in ----------

def make_step(position: int, operation: str, **kwargs) -> dict:
    """1 buoc dang dict - formatter doc duoc ca model SQLAlchemy lan dict."""
    step = {
        "position": position,
        "operation": operation,
        "time_min": None, "time_max": None, "time_unit": None,
        "temp_mode": "none", "temp_min": None, "temp_max": None,
        "ph_min": None, "ph_max": None,
        "time_text": None, "temp_text": None, "ph_text": None,
        "concentrations": [], "chemicals": [],
    }
    step.update(kwargs)
    return step


def make_concentration(component=None, value_min=None, value_max=None, unit=None, text_override=None) -> dict:
    return {
        "component": component, "value_min": value_min, "value_max": value_max,
        "unit": unit, "text_override": text_override,
    }


def make_chemical(display_name: str) -> dict:
    return {"display_name": display_name, "product_id": None, "lab_chemical_id": None}


def make_process(steps, **kwargs) -> dict:
    process = {
        "code": "LT-2026-001",
        "customer_name": "Nhà máy Z-113",
        "requirement": "sản phẩm sau xử lý có màu xanh than-xanh xám",
        "sample_quantity": 2,
        "test_month": date(2026, 8, 1),
        "prepared_by": "Vũ Thị Oanh",
        "steps": steps,
    }
    process.update(kwargs)
    return process


@pytest.fixture
def sample_steps():
    """Buoc 2 va buoc 4 cua LT-2026-001 - 2 truong hop nhieu chi tiet nhat."""
    return [
        make_step(
            1, "Mạ kẽm kiềm",
            time_min=50, time_unit="min",
            temp_mode="range", temp_min=20, temp_max=30,
            concentrations=[
                make_concentration("Zn^2+", 8, 16, "g/l"),
                make_concentration("NaOH", 110, 160, "g/l"),
            ],
            chemicals=[make_chemical(c) for c in ("NCZ-48A", "NCZ-48B", "NCZ-48C", "NCZ-48R")],
        ),
        make_step(
            2, "Tẩy sáng",
            time_min=3, time_max=5, time_unit="sec",
            concentrations=[make_concentration(None, 0.5, None, "%")],
            chemicals=[make_chemical("HNO_3")],
        ),
    ]


# ---------- DB rieng cho test ----------

# Cac bang test duoc don sach giua moi test. Xep theo thu tu xoa duoc (con truoc cha).
MANAGED_TABLES = (
    "dispatch.delivery_trips",
    "dispatch.drivers",
    "dispatch.vehicles",
    "warehouse.dispatch_items",
    "warehouse.dispatches",
    "warehouse.receipt_items",
    "warehouse.receipts",
    "warehouse.stock_items",
    "warehouse.audits",
    "warehouse.locations",
    "accounting.invoice_items",
    "accounting.vouchers",
    "accounting.invoices",
    "accounting.bank_accounts",
    "hr.attendance",
    "hr.leave_requests",
    "hr.contracts",
    "hr.certificates",
    "hr.employees",
    "hr.departments",
    "lab.test_process_step_concentrations",
    "lab.test_process_step_chemicals",
    "lab.test_process_steps",
    "lab.test_processes",
    "lab.process_templates",
    "common.company_profile",
    "website.contact_leads",
    "auth.users",
    "auth.roles",
    "auth.refresh_tokens",
    "auth.password_resets",
    "system.audit_logs",
)

TEST_ADMIN = {"identifier": "admin@test.local", "password": "matkhau-test-123"}


def _test_database_url() -> str:
    from app.core.config import settings

    url = make_url(settings.database_url)
    return url.set(database=f"{url.database}_test").render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def test_engine():
    try:
        from alembic import command
        from alembic.config import Config
    except ImportError:
        pytest.skip("Alembic chưa được cài đặt; bỏ qua các bài test cần database.")

    url = make_url(_test_database_url())
    assert url.database.endswith("_test"), "Test phai chay tren DB co duoi _test"

    # Tao DB test neu chua co (CREATE DATABASE khong chay trong transaction)
    # Truyen thang URL: str(url) cua SQLAlchemy 2 che mat khau thanh "***"
    try:
        admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
        with admin.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database}
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{url.database}"'))
        admin.dispose()

        # Dung DB test bang chinh cac migration cua Alembic - cung duong voi DB that
        config = Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))
        config.set_main_option("script_location", str(Path(__file__).resolve().parent.parent / "migrations"))
        config.set_main_option("sqlalchemy.url", url.render_as_string(hide_password=False))
        command.upgrade(config, "head")

        engine = create_engine(url, pool_pre_ping=True)
    except Exception as exc:
        pytest.skip(f"Không thể kết nối cơ sở dữ liệu test ({exc}); bỏ qua test cần database.")

    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Session tro vao DB test, da don sach bang truoc moi test."""
    assert test_engine.url.database.endswith("_test")
    with test_engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {', '.join(MANAGED_TABLES)} RESTART IDENTITY CASCADE"))

    factory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = factory()
    try:
        yield session
    finally:
        session.close()


def _make_user(db, email, password, permission_codes, require_2fa=False, employee_code=None):
    """Tai khoan tren DB test voi mot vai tro rieng giu dung cac quyen cho truoc."""
    from app.core.security import hash_password
    from app.modules.auth import models as auth_models

    permissions = db.query(auth_models.Permission).filter(auth_models.Permission.code.in_(permission_codes)).all()
    role = auth_models.Role(code=f"test_{len(db.query(auth_models.Role).all())}", name="Vai trò test",
                            require_2fa=require_2fa, permissions=permissions)
    user = auth_models.User(email=email, full_name="Người test", password_hash=hash_password(password),
                            employee_code=employee_code, roles=[role])
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def anon_client(db_session):
    """TestClient chua dang nhap, dung DB test thay cho DB that."""
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from app.main import app
    from app.modules.auth.permissions import sync_permissions
    from app.modules.system import service as audit_service

    sync_permissions(db_session)
    db_session.commit()
    app.dependency_overrides[get_db] = lambda: db_session
    real_factory = audit_service.audit_session_factory
    audit_service.audit_session_factory = sessionmaker(bind=db_session.get_bind())
    with TestClient(app) as test_client:
        yield test_client
    audit_service.audit_session_factory = real_factory
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(db_session):
    return lambda email, password, permissions, require_2fa=False, employee_code=None: _make_user(
        db_session, email, password, permissions, require_2fa, employee_code)


@pytest.fixture
def client(anon_client, make_user):
    """TestClient da dang nhap bang tai khoan toan quyen ("*", khong bat 2FA)."""
    make_user(TEST_ADMIN["identifier"], TEST_ADMIN["password"], ["*"])
    response = anon_client.post("/api/v1/auth/login", json=TEST_ADMIN)
    assert response.status_code == 200 and response.json()["step"] == "done", response.text
    return anon_client


@pytest.fixture
def process_payload():
    """Body toi thieu hop le cho POST /api/v1/lab/test-processes."""
    def build(**overrides):
        payload = {
            "customer_name": "Nhà máy Z-113",
            "requirement": "sản phẩm sau xử lý có màu xanh than-xanh xám",
            "sample_quantity": 2,
            "test_month": "2026-08-01",
            "prepared_by": "Vũ Thị Oanh",
            "status": "draft",
            "steps": [
                {"operation": "Tiền xử lí"},
                {
                    "operation": "Mạ kẽm kiềm",
                    "time_min": 50, "time_unit": "min",
                    "temp_mode": "range", "temp_min": 20, "temp_max": 30,
                    "concentrations": [
                        {"component": "Zn^2+", "value_min": 8, "value_max": 16, "unit": "g/l"},
                        {"component": "NaOH", "value_min": 110, "value_max": 160, "unit": "g/l"},
                    ],
                    "chemicals": [{"display_name": "NCZ-48A"}, {"display_name": "NCZ-48B"}],
                },
                {"operation": "Rửa nước", "time_min": 2, "time_max": 3,
                 "time_unit": "min", "temp_mode": "ambient"},
            ],
        }
        payload.update(overrides)
        return payload
    return build
