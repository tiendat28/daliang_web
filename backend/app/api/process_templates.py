"""Quy trinh chuan = bo buoc dung lai cho nhieu luu trinh.

Cac buoc luu thang trong cot jsonb `steps`, cung cau truc voi mang steps cua
API luu trinh, nen "Chen tu quy trinh chuan" ben FE chi viec do nguyen vao form.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.common import get_or_404
from app.core.database import get_db

router = APIRouter(prefix="/api/process-templates", tags=["process-templates"])

NOT_FOUND = "Khong tim thay quy trinh chuan"


def template_out(template: models.ProcessTemplate) -> schemas.ProcessTemplateOut:
    out = schemas.ProcessTemplateOut.model_validate(template)
    steps = template.steps or []
    out.step_count = len(steps)
    out.operations = [step.get("operation", "") for step in steps]
    return out


def _check_name_free(db: Session, name: str, exclude_id: int | None = None) -> None:
    query = db.query(models.ProcessTemplate).filter(models.ProcessTemplate.name == name)
    if exclude_id is not None:
        query = query.filter(models.ProcessTemplate.id != exclude_id)
    if query.first():
        raise HTTPException(409, f"Đã có quy trình chuẩn tên \"{name}\", đổi tên khác")


@router.get("", response_model=list[schemas.ProcessTemplateOut])
def list_process_templates(db: Session = Depends(get_db)):
    templates = db.query(models.ProcessTemplate).order_by(models.ProcessTemplate.name).all()
    return [template_out(t) for t in templates]


@router.get("/{template_id}", response_model=schemas.ProcessTemplateOut)
def get_process_template(template_id: int, db: Session = Depends(get_db)):
    return template_out(get_or_404(db, models.ProcessTemplate, template_id, NOT_FOUND))


@router.post("", response_model=schemas.ProcessTemplateOut, status_code=201)
def create_process_template(payload: schemas.ProcessTemplateCreate, db: Session = Depends(get_db)):
    _check_name_free(db, payload.name)
    template = models.ProcessTemplate(
        name=payload.name,
        description=payload.description,
        steps=[step.model_dump(mode="json") for step in payload.steps],
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template_out(template)


@router.put("/{template_id}", response_model=schemas.ProcessTemplateOut)
def update_process_template(template_id: int, payload: schemas.ProcessTemplateUpdate, db: Session = Depends(get_db)):
    template = get_or_404(db, models.ProcessTemplate, template_id, NOT_FOUND)
    _check_name_free(db, payload.name, exclude_id=template_id)
    template.name = payload.name
    template.description = payload.description
    template.steps = [step.model_dump(mode="json") for step in payload.steps]
    db.commit()
    db.refresh(template)
    return template_out(template)


@router.delete("/{template_id}")
def delete_process_template(template_id: int, db: Session = Depends(get_db)):
    template = get_or_404(db, models.ProcessTemplate, template_id, NOT_FOUND)
    db.delete(template)
    db.commit()
    return {"ok": True}
