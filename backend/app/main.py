"""Backend chung cua ca he thong: moi API nam duoi /api/v1/<module>/.

Cau truc DB do Alembic quan ly (`alembic upgrade head` chay truoc khi khoi
dong, xem Dockerfile) - app KHONG tu tao/sua bang.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import API_PREFIX, DEV_JWT_SECRET, STATIC_DIR, settings
from app.core.database import SessionLocal, engine
from app.modules import load_all_modules, module_routers
from app.modules.auth.permissions import sync_permissions
from app.modules.common.services.company_profile import seed_company_profile
from app.modules.system.service import AuditMiddleware
from app.modules.website.seed import seed_website

load_all_modules()

if settings.cookie_secure and settings.jwt_secret == DEV_JWT_SECRET:
    # Chay HTTPS (that) ma quen dat JWT_SECRET: ai biet khoa mac dinh deu gia duoc phien dang nhap
    raise RuntimeError("Chua dat bien moi truong JWT_SECRET cho moi truong that")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Du lieu mac dinh, idempotent: chi dien cho con trong, khong ghi de
    seed_company_profile(engine)
    seed_website(engine)
    with SessionLocal() as db:
        sync_permissions(db)   # quyen khai trong code -> bang auth.permissions (+ vai tro lan dau)
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
