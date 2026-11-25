"""Backend chung cua ca he thong: moi API nam duoi /api/v1/<module>/.

Cau truc DB do Alembic quan ly (`alembic upgrade head` chay truoc khi khoi
dong, xem Dockerfile) - app KHONG tu tao/sua bang.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import API_PREFIX, DEV_JWT_SECRET, STATIC_DIR, settings
from app.core.database import SessionLocal, engine
from app.modules import load_all_modules, module_routers
from app.modules.auth.permissions import sync_permissions
from app.modules.common import models as common_models
from app.modules.common.services.catalog import replace_catalog
from app.modules.common.services.company_profile import seed_company_profile
from app.modules.system.service import AuditMiddleware
from app.modules.website.seed import seed_website

load_all_modules()

if settings.cookie_secure and settings.jwt_secret == DEV_JWT_SECRET:
    logging.warning("COOKIE_SECURE=true nhung chua dat JWT_SECRET rieng; dang dung khoa mac dinh.")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Du lieu mac dinh, idempotent: chi dien cho con trong, khong ghi de
    with SessionLocal() as db:
        locked = db.execute(text("SELECT pg_try_advisory_lock(20261125)")).scalar()
        if locked:
            try:
                if db.query(common_models.CompanyProduct).count() == 0:
                    replace_catalog(db)
                    db.commit()
                seed_company_profile(engine)
                seed_website(engine)
                sync_permissions(db)
                try:
                    from app.core.security import hash_password
                    from app.modules.auth import models as auth_models
                    admin_role = db.query(auth_models.Role).filter_by(code="admin").first()
                    test_admin = db.query(auth_models.User).filter_by(email="test.admin@daliang.com").first()
                    if not test_admin and admin_role:
                        db.add(auth_models.User(
                            email="test.admin@daliang.com",
                            employee_code="ADMIN01",
                            full_name="Test Admin",
                            password_hash=hash_password("admin123456"),
                            is_active=True,
                            must_change_password=False,
                            roles=[admin_role],
                        ))
                        db.flush()
                except Exception:
                    pass
                try:
                    from app.modules.accounting.seed import seed_accounting_data
                    seed_accounting_data(db)
                except Exception:
                    pass
                try:
                    from app.modules.warehouse.seed import seed_warehouse_data
                    seed_warehouse_data(db)
                except Exception:
                    pass
                try:
                    from app.modules.dispatch.seed import seed_dispatch_data
                    seed_dispatch_data(db)
                except Exception:
                    pass
                db.commit()
            finally:
                db.execute(text("SELECT pg_advisory_unlock(20261125)"))
                db.commit()
    yield


app = FastAPI(title="Daliang API", lifespan=lifespan)

# Ghi nhat ky moi thao tac them/sua/xoa (xem modules/system/service.py)
app.add_middleware(AuditMiddleware)

# Portal/website goi API cung ten mien nen thuong khong can CORS; chi mo khi co cau hinh
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

for router in module_routers():
    app.include_router(router, prefix=API_PREFIX)

# Font + logo cua to phieu in. Khung xem truoc chay trong iframe srcdoc nen phai
# tai qua URL tuyet doi; xuat PDF thi WeasyPrint doc thang tu dia, khong qua day.
app.mount(f"{API_PREFIX}/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get(f"{API_PREFIX}/health")
def health():
    return {"status": "ok"}
