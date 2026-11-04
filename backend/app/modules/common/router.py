"""API du lieu dung chung - /api/v1/common/...

Quyen: GET `.view`, POST `.create`, PUT/PATCH `.update`, DELETE `.delete` (xem auth.deps.guard).
"""
from fastapi import APIRouter, Depends

from app.modules.auth.deps import guard
from app.modules.common.routers import company_profile, customers, documents, products

router = APIRouter(prefix="/common")
for part, resource, overrides in (
    (customers, "common.customers", None),
    (products, "common.products", None),
    (company_profile, "common.company_profile", {"/logo": "update"}),   # doi logo = sua
    (documents, "common.documents", None),
):
    router.include_router(part.router, dependencies=[Depends(guard(resource, overrides))])
