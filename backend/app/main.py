from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
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
)

Base.metadata.create_all(bind=engine)

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


@app.get("/api/health")
def health():
    return {"status": "ok"}
