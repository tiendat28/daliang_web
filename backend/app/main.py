from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.core.migrations import run_startup_migrations
from app.api import (
    customers,
    company_products,
    lab_chemicals,
    indicators,
    equipment,
    chemical_orders,
    chemical_sampling,
    analysis_reports,
    work_logs,
    documents,
    test_processes,
    process_templates,
    company_profile,
)
from app.core.seed import seed_company_profile
from app.services.test_process_sheet import STATIC_DIR

Base.metadata.create_all(bind=engine)
run_startup_migrations(engine)
seed_company_profile(engine)

app = FastAPI(title="Lab Chemical Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)
app.include_router(company_products.router)
app.include_router(lab_chemicals.router)
app.include_router(indicators.router)
app.include_router(equipment.router)
app.include_router(chemical_orders.router)
app.include_router(chemical_sampling.router)
app.include_router(analysis_reports.router)
app.include_router(work_logs.router)
app.include_router(documents.router)
app.include_router(test_processes.router)
app.include_router(process_templates.router)
app.include_router(company_profile.router)

# Font + logo cua to phieu in. Khung xem truoc chay trong iframe srcdoc nen phai
# tai qua URL tuyet doi; xuat PDF thi WeasyPrint doc thang tu dia, khong qua day.
app.mount("/api/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/api/health")
def health():
    return {"status": "ok"}
