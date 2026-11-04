"""API module ky thuat - /api/v1/lab/...

Quyen: GET `.view`, POST `.create`, PUT/PATCH `.update`, DELETE `.delete` (xem auth.deps.guard).
"""
from fastapi import APIRouter, Depends

from app.modules.auth.deps import guard
from app.modules.lab.routers import (
    analysis_reports, chemicals, equipment, formulations, indicators,
    process_templates, samples, test_processes, work_logs,
)

router = APIRouter(prefix="/lab")
# POST khong phai "them": xem truoc to in chi la xem, mo hop moi la sua ton kho
PREVIEWS = {"/preview-sheet": "view", "/letterhead-preview": "view"}

for part, resource, overrides in (
    (chemicals, "lab.chemicals", {"/open-box": "update"}),
    (indicators, "lab.indicators", None),
    (equipment, "lab.equipment", None),
    (formulations, "lab.formulations", None),
    (samples, "lab.samples", None),
    (analysis_reports, "lab.analysis_reports", None),
    (work_logs, "lab.work_logs", None),
    (test_processes, "lab.test_processes", PREVIEWS),
    (process_templates, "lab.process_templates", None),
):
    router.include_router(part.router, dependencies=[Depends(guard(resource, overrides))])
