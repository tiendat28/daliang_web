"""API nhan su - ho so, cham cong, nghi phep, hop dong, chung chi."""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.crud import apply_payload, get_or_404
from app.core.database import get_db
from app.modules.auth.deps import guard
from app.modules.hr import models, schemas

router = APIRouter(prefix="/hr", tags=["hr"])


def employee_out(row: models.EmployeeProfile) -> schemas.EmployeeOut:
    data = schemas.EmployeeOut.model_validate(row)
    data.department_name = row.department_record.name if row.department_record else row.department_code
    return data


def attendance_out(row: models.Attendance) -> schemas.AttendanceOut:
    data = schemas.AttendanceOut.model_validate(row)
    data.employee_name = row.employee.full_name if row.employee else None
    return data


def leave_out(row: models.LeaveRequest) -> schemas.LeaveRequestOut:
    data = schemas.LeaveRequestOut.model_validate(row)
    data.employee_name = row.employee.full_name if row.employee else None
    return data


def contract_out(row: models.Contract) -> schemas.ContractOut:
    data = schemas.ContractOut.model_validate(row)
    data.employee_name = row.employee.full_name if row.employee else None
    return data


def certificate_out(row: models.Certificate) -> schemas.CertificateOut:
    data = schemas.CertificateOut.model_validate(row)
    data.employee_name = row.employee.full_name if row.employee else None
    return data


def _get_employee_or_404(db: Session, employee_id: int) -> models.EmployeeProfile:
    return get_or_404(db, models.EmployeeProfile, employee_id, "Không tìm thấy nhân viên")


# ---------- Dashboard ----------

@router.get("/dashboard", response_model=schemas.HrDashboardOut, dependencies=[Depends(guard("hr.employees"))])
def dashboard(db: Session = Depends(get_db)):
    today = date.today()
    soon = today + timedelta(days=45)
    employees = (
        db.query(models.EmployeeProfile)
        .options(joinedload(models.EmployeeProfile.department_record))
        .order_by(models.EmployeeProfile.full_name)
        .all()
    )
    active = [row for row in employees if row.status == "active"]
    present = db.query(models.Attendance).filter(
        models.Attendance.work_date == today,
        models.Attendance.status == "present",
    ).count()
    leave_today_rows = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.status == "approved",
        models.LeaveRequest.start_date <= today,
        models.LeaveRequest.end_date >= today,
    ).all()
    pending = (
        db.query(models.LeaveRequest)
        .options(joinedload(models.LeaveRequest.employee))
        .filter(models.LeaveRequest.status == "pending")
        .order_by(models.LeaveRequest.created_at.desc())
        .all()
    )
    expiring_contracts = db.query(models.Contract).filter(
        models.Contract.status == "active",
        models.Contract.end_date.isnot(None),
        models.Contract.end_date >= today,
        models.Contract.end_date <= soon,
    ).count()
    expiring_certs = (
        db.query(models.Certificate)
        .options(joinedload(models.Certificate.employee))
        .filter(
            models.Certificate.expires_at.isnot(None),
            models.Certificate.expires_at >= today,
            models.Certificate.expires_at <= today + timedelta(days=30),
        )
        .all()
    )
    return schemas.HrDashboardOut(
        total_employees=len(employees),
        active_employees=len(active),
        present_today=present,
        leave_today=len(leave_today_rows),
        pending_leave_requests=len(pending),
        contracts_expiring=expiring_contracts,
        certificates_expiring=len(expiring_certs),
        employees=[employee_out(row) for row in employees],
        pending_leaves=[leave_out(row) for row in pending[:5]],
        expiring_certificates=[certificate_out(row) for row in expiring_certs[:5]],
    )


# ---------- Hồ sơ nhân viên ----------

@router.get("/employees", response_model=list[schemas.EmployeeOut], dependencies=[Depends(guard("hr.employees"))])
def list_employees(
    db: Session = Depends(get_db),
    status: str | None = None,
    department: str | None = None,
):
    query = (
        db.query(models.EmployeeProfile)
        .options(joinedload(models.EmployeeProfile.department_record))
        .order_by(models.EmployeeProfile.full_name)
    )
    if status:
        query = query.filter(models.EmployeeProfile.status == status)
    if department:
        query = query.filter(models.EmployeeProfile.department_code == department)
    return [employee_out(row) for row in query.all()]


@router.post("/employees", response_model=schemas.EmployeeOut, status_code=201, dependencies=[Depends(guard("hr.employees"))])
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    if db.query(models.EmployeeProfile).filter(models.EmployeeProfile.employee_code == payload.employee_code).first():
        raise HTTPException(400, "Mã nhân viên đã tồn tại")
    row = models.EmployeeProfile(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return employee_out(row)


@router.put("/employees/{employee_id}", response_model=schemas.EmployeeOut, dependencies=[Depends(guard("hr.employees"))])
def update_employee(employee_id: int, payload: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    row = _get_employee_or_404(db, employee_id)
    duplicate = db.query(models.EmployeeProfile).filter(
        models.EmployeeProfile.employee_code == payload.employee_code,
        models.EmployeeProfile.id != employee_id,
    ).first()
    if duplicate:
        raise HTTPException(400, "Mã nhân viên đã tồn tại")
    apply_payload(row, payload)
    db.commit()
    db.refresh(row)
    return employee_out(row)


@router.delete("/employees/{employee_id}", dependencies=[Depends(guard("hr.employees"))])
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    row = _get_employee_or_404(db, employee_id)
    db.delete(row)
    db.commit()
    return {"ok": True}


# ---------- Phòng ban ----------

@router.get("/departments", response_model=list[schemas.DepartmentOut], dependencies=[Depends(guard("hr.departments"))])
def list_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).filter(models.Department.is_active.is_(True)).order_by(models.Department.name).all()


@router.post("/departments", response_model=schemas.DepartmentOut, status_code=201, dependencies=[Depends(guard("hr.departments"))])
def create_department(payload: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    if db.query(models.Department).filter(models.Department.code == payload.code).first():
        raise HTTPException(400, "Mã phòng ban đã tồn tại")
    row = models.Department(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/departments/{department_id}", response_model=schemas.DepartmentOut, dependencies=[Depends(guard("hr.departments"))])
def update_department(department_id: int, payload: schemas.DepartmentUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, models.Department, department_id, "Không tìm thấy phòng ban")
    duplicate = db.query(models.Department).filter(
        models.Department.code == payload.code,
        models.Department.id != department_id,
    ).first()
    if duplicate:
        raise HTTPException(400, "Mã phòng ban đã tồn tại")
    apply_payload(row, payload)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/departments/{department_id}", dependencies=[Depends(guard("hr.departments"))])
def delete_department(department_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, models.Department, department_id, "Không tìm thấy phòng ban")
    row.is_active = False
    db.commit()
    return {"ok": True}


# ---------- Chấm công ----------

@router.get("/attendance", response_model=list[schemas.AttendanceOut], dependencies=[Depends(guard("hr.attendance"))])
def list_attendance(db: Session = Depends(get_db), work_date: date | None = None):
    query = (
        db.query(models.Attendance)
        .options(joinedload(models.Attendance.employee))
        .order_by(models.Attendance.work_date.desc(), models.Attendance.id.desc())
    )
    if work_date:
        query = query.filter(models.Attendance.work_date == work_date)
    return [attendance_out(row) for row in query.limit(500).all()]


@router.post("/attendance", response_model=schemas.AttendanceOut, status_code=201, dependencies=[Depends(guard("hr.attendance"))])
def create_attendance(payload: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    _get_employee_or_404(db, payload.employee_id)
    row = models.Attendance(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return attendance_out(row)


@router.put("/attendance/{attendance_id}", response_model=schemas.AttendanceOut, dependencies=[Depends(guard("hr.attendance"))])
def update_attendance(attendance_id: int, payload: schemas.AttendanceUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, models.Attendance, attendance_id, "Không tìm thấy bản ghi chấm công")
    apply_payload(row, payload)
    db.commit()
    db.refresh(row)
    return attendance_out(row)


@router.delete("/attendance/{attendance_id}", dependencies=[Depends(guard("hr.attendance"))])
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, models.Attendance, attendance_id, "Không tìm thấy bản ghi chấm công")
    db.delete(row)
    db.commit()
    return {"ok": True}


# ---------- Nghỉ phép ----------

@router.get("/leave-requests", response_model=list[schemas.LeaveRequestOut], dependencies=[Depends(guard("hr.leave_requests"))])
def list_leave_requests(db: Session = Depends(get_db), status: str | None = None):
    query = (
        db.query(models.LeaveRequest)
        .options(joinedload(models.LeaveRequest.employee))
        .order_by(models.LeaveRequest.created_at.desc())
    )
    if status:
        query = query.filter(models.LeaveRequest.status == status)
    return [leave_out(row) for row in query.all()]


@router.post("/leave-requests", response_model=schemas.LeaveRequestOut, status_code=201, dependencies=[Depends(guard("hr.leave_requests"))])
def create_leave_request(payload: schemas.LeaveRequestCreate, db: Session = Depends(get_db)):
    _get_employee_or_404(db, payload.employee_id)
    row = models.LeaveRequest(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return leave_out(row)


@router.patch("/leave-requests/{request_id}/decision", response_model=schemas.LeaveRequestOut, dependencies=[Depends(guard("hr.leave_requests", {"/decision": "approve"}))])
def decide_leave_request(request_id: int, payload: schemas.LeaveDecisionIn, db: Session = Depends(get_db)):
    row = get_or_404(db, models.LeaveRequest, request_id, "Không tìm thấy đơn nghỉ phép")
    row.status = payload.status
    row.reviewed_at = datetime.now().astimezone()
    db.commit()
    db.refresh(row)
    return leave_out(row)


@router.delete("/leave-requests/{request_id}", dependencies=[Depends(guard("hr.leave_requests"))])
def delete_leave_request(request_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, models.LeaveRequest, request_id, "Không tìm thấy đơn nghỉ phép")
    db.delete(row)
    db.commit()
    return {"ok": True}


# ---------- Hợp đồng ----------

@router.get("/contracts", response_model=list[schemas.ContractOut], dependencies=[Depends(guard("hr.contracts"))])
def list_contracts(db: Session = Depends(get_db)):
    query = db.query(models.Contract).options(joinedload(models.Contract.employee)).order_by(models.Contract.end_date)
    return [contract_out(row) for row in query.all()]


@router.post("/contracts", response_model=schemas.ContractOut, status_code=201, dependencies=[Depends(guard("hr.contracts"))])
def create_contract(payload: schemas.ContractCreate, db: Session = Depends(get_db)):
    _get_employee_or_404(db, payload.employee_id)
    row = models.Contract(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return contract_out(row)


@router.put("/contracts/{contract_id}", response_model=schemas.ContractOut, dependencies=[Depends(guard("hr.contracts"))])
def update_contract(contract_id: int, payload: schemas.ContractUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, models.Contract, contract_id, "Không tìm thấy hợp đồng")
    apply_payload(row, payload)
    db.commit()
    db.refresh(row)
    return contract_out(row)


@router.delete("/contracts/{contract_id}", dependencies=[Depends(guard("hr.contracts"))])
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, models.Contract, contract_id, "Không tìm thấy hợp đồng")
    db.delete(row)
    db.commit()
    return {"ok": True}


# ---------- Chứng chỉ ----------

@router.get("/certificates", response_model=list[schemas.CertificateOut], dependencies=[Depends(guard("hr.certificates"))])
def list_certificates(db: Session = Depends(get_db)):
    query = db.query(models.Certificate).options(joinedload(models.Certificate.employee)).order_by(models.Certificate.expires_at)
    return [certificate_out(row) for row in query.all()]


@router.post("/certificates", response_model=schemas.CertificateOut, status_code=201, dependencies=[Depends(guard("hr.certificates"))])
def create_certificate(payload: schemas.CertificateCreate, db: Session = Depends(get_db)):
    _get_employee_or_404(db, payload.employee_id)
    row = models.Certificate(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return certificate_out(row)


@router.put("/certificates/{certificate_id}", response_model=schemas.CertificateOut, dependencies=[Depends(guard("hr.certificates"))])
def update_certificate(certificate_id: int, payload: schemas.CertificateUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, models.Certificate, certificate_id, "Không tìm thấy chứng chỉ")
    apply_payload(row, payload)
    db.commit()
    db.refresh(row)
    return certificate_out(row)


@router.delete("/certificates/{certificate_id}", dependencies=[Depends(guard("hr.certificates"))])
def delete_certificate(certificate_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, models.Certificate, certificate_id, "Không tìm thấy chứng chỉ")
    db.delete(row)
    db.commit()
    return {"ok": True}
