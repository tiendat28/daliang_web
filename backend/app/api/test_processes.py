"""Luu trinh test mau.

Luu y thu tu khai bao: cac route tinh (`preview-sheet`, `operation-suggestions`,
`last-step`) phai dat TRUOC `/{process_id}`, khong thi FastAPI coi "last-step"
la mot process_id va tra 422.
"""
from datetime import date
from urllib.parse import quote

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.api.common import apply_payload
from app.core.database import get_db
from app.services.test_process_code import next_process_code
from app.services.test_process_format import fold_accents, step_display, strip_markers
from app.services.test_process_sheet import pdf_filename, render_sheet_html, render_sheet_pdf

router = APIRouter(prefix="/api/test-processes", tags=["test-processes"])

NOT_FOUND = "Khong tim thay luu trinh test mau"

# Toi da 5 ten hoa chat tren moi dong danh sach (muc 4 cua dac ta)
MAX_CHEMICAL_NAMES = 5

# Goi y san cho o "Hang muc", tron voi cac ten da tung dung trong DB
DEFAULT_OPERATIONS = [
    "Tiền xử lí", "Tẩy dầu", "Tẩy gỉ", "Hoạt hóa", "Mạ kẽm kiềm", "Mạ kẽm acid",
    "Rửa nước", "Rửa nước x2", "Tẩy sáng", "Thụ động", "Nhuộm màu", "Phủ bảo vệ", "Sấy",
]

SORTABLE = {
    "test_month": models.TestProcess.test_month,
    "code": models.TestProcess.code,
    "customer_name": models.TestProcess.customer_name,
    "updated_at": models.TestProcess.updated_at,
    "status": models.TestProcess.status,
}
DEFAULT_SORT = "-test_month"

# selectinload chu khong joinedload: hai bang con cung nap bang JOIN se nhan
# cheo nhau (n nong do x m hoa chat cho moi buoc); selectinload chi them 3 cau
# truy van phu cho ca trang.
_LOAD_OPTIONS = (
    selectinload(models.TestProcess.steps).selectinload(models.TestProcessStep.concentrations),
    selectinload(models.TestProcess.steps).selectinload(models.TestProcessStep.chemicals),
)

_unaccent_available: bool | None = None


# ---------- Tien ich dung chung ----------

def _alive(query):
    """Bo qua ban ghi da xoa mem."""
    return query.filter(models.TestProcess.deleted_at.is_(None))


def get_process_or_404(db: Session, process_id: int) -> models.TestProcess:
    process = _alive(
        db.query(models.TestProcess).options(*_LOAD_OPTIONS)
        .filter(models.TestProcess.id == process_id)
    ).first()
    if not process:
        raise HTTPException(404, NOT_FOUND)
    return process


def get_company_profile(db: Session) -> models.CompanyProfile | None:
    """Letterhead dung chung. Chua co dong nao thi template tu dung gia tri mac dinh."""
    return db.query(models.CompanyProfile).order_by(models.CompanyProfile.id).first()


def _has_unaccent(db: Session) -> bool:
    """DB co extension unaccent khong (do mot lan roi nho lai).

    Khong co (khong du quyen tren DB dung chung) thi lui ve so sanh co dau -
    van tim duoc, chi la phai go dung dau.
    """
    global _unaccent_available
    if _unaccent_available is None:
        try:
            db.execute(select(func.unaccent("a")))
            _unaccent_available = True
        except Exception:  # noqa: BLE001
            db.rollback()
            _unaccent_available = False
    return _unaccent_available


def _normalized(db: Session, column):
    """Cot da ha chu thuong va bo dau, de tim "nha may z-113" ra "Nhà máy Z-113"."""
    lowered = func.lower(column)
    return func.unaccent(lowered) if _has_unaccent(db) else lowered


def _needle(db: Session, text: str):
    """Chuoi tim, xu ly cung kieu voi cot de hai ben luon so sanh cung he."""
    return func.unaccent(text) if _has_unaccent(db) else text


def _apply_steps(db: Session, process: models.TestProcess, steps_in) -> None:
    """Thay toan bo cac buoc. Goi trong transaction cua caller."""
    for step in list(process.steps):
        db.delete(step)
    db.flush()

    for position, step_in in enumerate(steps_in, start=1):
        step = models.TestProcessStep(
            process_id=process.id,
            position=position,
            operation=step_in.operation,
            time_min=step_in.time_min, time_max=step_in.time_max, time_unit=step_in.time_unit,
            temp_mode=step_in.temp_mode.value, temp_min=step_in.temp_min, temp_max=step_in.temp_max,
            ph_min=step_in.ph_min, ph_max=step_in.ph_max,
            time_text=step_in.time_text, temp_text=step_in.temp_text, ph_text=step_in.ph_text,
            note=step_in.note,
        )
        db.add(step)
        db.flush()

        for index, row in enumerate(step_in.concentrations, start=1):
            db.add(models.TestProcessStepConcentration(
                step_id=step.id, position=index, component=row.component,
                value_min=row.value_min, value_max=row.value_max,
                unit=row.unit, text_override=row.text_override,
            ))
        for index, row in enumerate(step_in.chemicals, start=1):
            db.add(models.TestProcessStepChemical(
                step_id=step.id, position=index, product_id=row.product_id,
                lab_chemical_id=row.lab_chemical_id, display_name=row.display_name,
            ))


def _detail(process: models.TestProcess) -> schemas.TestProcessDetailOut:
    out = schemas.TestProcessDetailOut.model_validate(process)
    out.source_process_code = process.source_process.code if process.source_process else None
    for step_out, step in zip(out.steps, process.steps):
        step_out.display = step_display(step)
    return out


def _step_to_dict(step: models.TestProcessStep) -> dict:
    """1 buoc dang jsonb - dung cho process_templates.steps va nut "dien theo lan gan nhat"."""
    return {
        "operation": step.operation,
        "time_min": float(step.time_min) if step.time_min is not None else None,
        "time_max": float(step.time_max) if step.time_max is not None else None,
        "time_unit": step.time_unit,
        "temp_mode": step.temp_mode,
        "temp_min": float(step.temp_min) if step.temp_min is not None else None,
        "temp_max": float(step.temp_max) if step.temp_max is not None else None,
        "ph_min": float(step.ph_min) if step.ph_min is not None else None,
        "ph_max": float(step.ph_max) if step.ph_max is not None else None,
        "time_text": step.time_text, "temp_text": step.temp_text, "ph_text": step.ph_text,
        "note": step.note,
        "concentrations": [
            {
                "component": c.component,
                "value_min": float(c.value_min) if c.value_min is not None else None,
                "value_max": float(c.value_max) if c.value_max is not None else None,
                "unit": c.unit, "text_override": c.text_override,
            }
            for c in step.concentrations
        ],
        "chemicals": [
            {"product_id": c.product_id, "lab_chemical_id": c.lab_chemical_id,
             "display_name": c.display_name}
            for c in step.chemicals
        ],
    }


# ---------- Danh sach ----------

@router.get("", response_model=schemas.TestProcessPage)
def list_test_processes(
    q: str | None = Query(None, description="Tim theo ma, khach hang, yeu cau, ten hoa chat"),
    status: schemas.TestProcessStatus | None = None,
    customer_id: int | None = None,
    product_id: int | None = Query(None, description="Chi lay luu trinh co dung san pham nay"),
    month_from: date | None = None,
    month_to: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = DEFAULT_SORT,
    db: Session = Depends(get_db),
):
    # Nap san cac bang con: _list_item duyet steps/chemicals cua tung dong, khong
    # co options nay thi moi lan mo trang la vai tram cau truy van con.
    query = _alive(db.query(models.TestProcess).options(*_LOAD_OPTIONS))

    if status:
        query = query.filter(models.TestProcess.status == status.value)
    if customer_id:
        query = query.filter(models.TestProcess.customer_id == customer_id)
    if month_from:
        query = query.filter(models.TestProcess.test_month >= month_from.replace(day=1))
    if month_to:
        query = query.filter(models.TestProcess.test_month <= month_to.replace(day=1))

    if product_id:
        query = query.filter(models.TestProcess.id.in_(
            select(models.TestProcessStep.process_id)
            .join(models.TestProcessStepChemical,
                  models.TestProcessStepChemical.step_id == models.TestProcessStep.id)
            .where(models.TestProcessStepChemical.product_id == product_id)
        ))

    if q and q.strip():
        needle = f"%{q.strip().lower()}%"
        chemical_match = (
            select(models.TestProcessStep.process_id)
            .join(models.TestProcessStepChemical,
                  models.TestProcessStepChemical.step_id == models.TestProcessStep.id)
            .where(_normalized(db, models.TestProcessStepChemical.display_name).like(_needle(db, needle)))
        )
        query = query.filter(or_(
            _normalized(db, models.TestProcess.code).like(_needle(db, needle)),
            _normalized(db, models.TestProcess.customer_name).like(_needle(db, needle)),
            _normalized(db, func.coalesce(models.TestProcess.requirement, "")).like(_needle(db, needle)),
            models.TestProcess.id.in_(chemical_match),
        ))

    total = query.count()

    descending = sort.startswith("-")
    column = SORTABLE.get(sort.lstrip("-"), SORTABLE["test_month"])
    order = column.desc() if descending else column.asc()
    # Chot thu tu bang id de phan trang khong nhay khi trung thang test
    rows = (
        query.order_by(order, models.TestProcess.id.desc())
        .offset((page - 1) * page_size).limit(page_size).all()
    )

    return schemas.TestProcessPage(
        items=[_list_item(db, row) for row in rows],
        total=total, page=page, page_size=page_size,
    )


def _list_item(db: Session, process: models.TestProcess) -> schemas.TestProcessListItem:
    item = schemas.TestProcessListItem.model_validate(process)
    item.step_count = len(process.steps)

    # Giu nguyen chu hoa/thuong nhu luc nhap (FE hien thanh chip "NCZ-48A"),
    # nhung so trung thi khong phan biet hoa thuong.
    names = []
    seen = set()
    for step in process.steps:
        for chemical in step.chemicals:
            name = strip_markers(chemical.display_name).strip()
            key = name.lower()
            if name and key not in seen:
                seen.add(key)
                names.append(name)
    item.chemical_count = len(names)
    item.chemical_names = names[:MAX_CHEMICAL_NAMES]
    return item


# ---------- Route tinh (phai dat truoc /{process_id}) ----------

@router.post("/preview-sheet", response_class=HTMLResponse)
def preview_sheet(payload: schemas.TestProcessWrite, db: Session = Depends(get_db)):
    """To A4 cho du lieu chua luu - dung khi dang go trong form."""
    process = payload.model_dump()
    process["code"] = ""
    # Buoc chua luu chua co id/position -> danh lai theo thu tu trong form
    process["steps"] = [
        {**step, "position": position}
        for position, step in enumerate(process.get("steps") or [], start=1)
    ]
    return HTMLResponse(render_sheet_html(process, get_company_profile(db), screen=True))


@router.get("/operation-suggestions", response_model=list[str])
def operation_suggestions(q: str | None = None, db: Session = Depends(get_db)):
    """Ten hang muc da dung + danh sach goi y san, cho autocomplete."""
    used = db.execute(
        select(models.TestProcessStep.operation)
        .join(models.TestProcess, models.TestProcess.id == models.TestProcessStep.process_id)
        .where(models.TestProcess.deleted_at.is_(None))
        .group_by(models.TestProcessStep.operation)
        .order_by(func.count().desc())
    ).scalars().all()

    result = []
    for name in list(used) + DEFAULT_OPERATIONS:
        if name and name not in result:
            result.append(name)

    if q and q.strip():
        needle = fold_accents(strip_markers(q)).strip().lower()
        result = [name for name in result if needle in fold_accents(name).lower()]
    return result


@router.get("/last-step", response_model=schemas.LastStepOut)
def last_step(operation: str, db: Session = Depends(get_db)):
    """Thong so cua lan gan nhat dung hang muc nay, cho nut "Dien theo lan gan nhat"."""
    step = (
        db.query(models.TestProcessStep)
        .join(models.TestProcess, models.TestProcess.id == models.TestProcessStep.process_id)
        .filter(models.TestProcess.deleted_at.is_(None))
        .filter(func.lower(models.TestProcessStep.operation) == (operation or "").strip().lower())
        .order_by(models.TestProcess.updated_at.desc(), models.TestProcessStep.id.desc())
        .first()
    )
    if not step:
        return schemas.LastStepOut(found=False)
    return schemas.LastStepOut(found=True, step=schemas.TestProcessStepIn(**_step_to_dict(step)))


# ---------- CRUD ----------

@router.post("", response_model=schemas.TestProcessDetailOut, status_code=201)
def create_test_process(payload: schemas.TestProcessCreate, db: Session = Depends(get_db)):
    process = models.TestProcess(
        code=next_process_code(db, payload.test_month.year),
        **payload.model_dump(exclude={"steps", "status"}),
        status=payload.status.value,
    )
    db.add(process)
    db.flush()
    _apply_steps(db, process, payload.steps)
    db.commit()
    db.refresh(process)
    return _detail(process)


@router.get("/{process_id}", response_model=schemas.TestProcessDetailOut)
def get_test_process(process_id: int, db: Session = Depends(get_db)):
    return _detail(get_process_or_404(db, process_id))


@router.put("/{process_id}", response_model=schemas.TestProcessDetailOut)
def update_test_process(process_id: int, payload: schemas.TestProcessUpdate, db: Session = Depends(get_db)):
    process = get_process_or_404(db, process_id)
    apply_payload(process, payload, exclude={"steps", "status"})
    process.status = payload.status.value
    _apply_steps(db, process, payload.steps)
    db.commit()
    db.refresh(process)
    return _detail(process)


@router.patch("/{process_id}/status", response_model=schemas.TestProcessDetailOut)
def set_status(process_id: int, payload: schemas.TestProcessStatusIn, db: Session = Depends(get_db)):
    process = get_process_or_404(db, process_id)
    process.status = payload.status.value
    db.commit()
    db.refresh(process)
    return _detail(process)


@router.post("/{process_id}/duplicate", response_model=schemas.TestProcessDetailOut, status_code=201)
def duplicate_test_process(process_id: int, db: Session = Depends(get_db)):
    """Ban sao: ma moi, trang thai Nhap, thang hien tai, nho lai luu trinh goc."""
    source = get_process_or_404(db, process_id)
    today = date.today()

    copy = models.TestProcess(
        code=next_process_code(db, today.year),
        customer_id=source.customer_id,
        customer_name=source.customer_name,
        requirement=source.requirement,
        sample_quantity=source.sample_quantity,
        test_month=today.replace(day=1),
        prepared_by=source.prepared_by,
        status=models.TestProcessStatus.draft.value,
        internal_note=source.internal_note,
        source_process_id=source.id,
    )
    db.add(copy)
    db.flush()

    # Chep buoc qua chung duong voi luc luu form, khoi phai nho rieng mot danh
    # sach truong nua moi khi them cot cho buoc
    _apply_steps(db, copy, [schemas.TestProcessStepIn(**_step_to_dict(step)) for step in source.steps])

    db.commit()
    db.refresh(copy)
    return _detail(copy)


@router.delete("/{process_id}")
def delete_test_process(process_id: int, db: Session = Depends(get_db)):
    """Xoa mem - ban ghi van con trong DB de truy lai duoc."""
    process = get_process_or_404(db, process_id)
    process.deleted_at = func.now()
    db.commit()
    return {"ok": True}


@router.post("/{process_id}/save-as-template", response_model=schemas.ProcessTemplateOut, status_code=201)
def save_as_template(
    process_id: int,
    payload: schemas.SaveAsTemplateIn = Body(...),
    db: Session = Depends(get_db),
):
    process = get_process_or_404(db, process_id)
    if db.query(models.ProcessTemplate).filter_by(name=payload.name).first():
        raise HTTPException(409, f"Đã có quy trình chuẩn tên \"{payload.name}\", đổi tên khác")

    template = models.ProcessTemplate(
        name=payload.name,
        description=payload.description or f"Lưu từ lưu trình {process.code}.",
        steps=[_step_to_dict(step) for step in process.steps],
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    from app.api.process_templates import template_out
    return template_out(template)


# ---------- To in ----------

@router.get("/{process_id}/sheet", response_class=HTMLResponse)
def get_test_process_sheet(process_id: int, db: Session = Depends(get_db)):
    """HTML to A4 cho khung xem truoc - cung template voi ban PDF."""
    process = get_process_or_404(db, process_id)
    return HTMLResponse(render_sheet_html(process, get_company_profile(db), screen=True))


@router.get("/{process_id}/pdf")
def get_test_process_pdf(
    process_id: int,
    download: int = Query(1, ge=0, le=1, description="1 = tai ve, 0 = mo trong tab moi de in"),
    db: Session = Depends(get_db),
):
    process = get_process_or_404(db, process_id)
    pdf = render_sheet_pdf(process, get_company_profile(db))
    filename = pdf_filename(process)
    disposition = "attachment" if download else "inline"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f"{disposition}; filename=\"{filename}\"; "
                f"filename*=UTF-8''{quote(filename)}"
            )
        },
    )
