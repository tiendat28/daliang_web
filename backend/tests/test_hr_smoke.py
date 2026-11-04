"""Unit and integration smoke tests for HR module."""
from datetime import date, time
import pytest
from pydantic import ValidationError

from app.modules.hr.schemas import (
    DepartmentCreate,
    EmployeeCreate,
    AttendanceCreate,
    LeaveRequestCreate,
    LeaveDecisionIn,
    ContractCreate,
    CertificateCreate,
    HrDashboardOut,
)


def test_department_schema_validation():
    dept = DepartmentCreate(code="QC", name="Phòng Quản lý chất lượng", is_active=True)
    assert dept.code == "QC"
    assert dept.name == "Phòng Quản lý chất lượng"
    assert dept.is_active is True

    # Empty code should raise ValidationError
    with pytest.raises(ValidationError):
        DepartmentCreate(code="", name="Tên")


def test_employee_schema_validation():
    emp = EmployeeCreate(
        employee_code="NV001",
        full_name="Nguyễn Văn A",
        email="a.nguyen@example.com",
        phone="0912345678",
        department_code="QC",
        position="Kỹ sư KCS",
        start_date=date(2026, 1, 1),
        status="active",
    )
    assert emp.employee_code == "NV001"
    assert emp.status == "active"

    # Empty full_name should fail
    with pytest.raises(ValidationError):
        EmployeeCreate(employee_code="NV002", full_name="")


def test_leave_request_date_range_validation():
    # Valid date range
    leave = LeaveRequestCreate(
        employee_id=1,
        leave_type="annual",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 5),
        reason="Nghỉ phép năm",
    )
    assert leave.end_date >= leave.start_date

    # Invalid range: end_date before start_date
    with pytest.raises(ValidationError) as exc_info:
        LeaveRequestCreate(
            employee_id=1,
            leave_type="annual",
            start_date=date(2026, 10, 5),
            end_date=date(2026, 10, 1),
        )
    assert "Ngày kết thúc phải sau hoặc bằng ngày bắt đầu" in str(exc_info.value)


def test_leave_decision_pattern_validation():
    ok_approved = LeaveDecisionIn(status="approved")
    assert ok_approved.status == "approved"

    ok_rejected = LeaveDecisionIn(status="rejected")
    assert ok_rejected.status == "rejected"

    with pytest.raises(ValidationError):
        LeaveDecisionIn(status="pending")

    with pytest.raises(ValidationError):
        LeaveDecisionIn(status="cancelled")


def test_attendance_and_contract_schemas():
    att = AttendanceCreate(
        employee_id=1,
        work_date=date(2026, 9, 28),
        check_in=time(8, 0),
        check_out=time(17, 0),
        status="present",
    )
    assert att.status == "present"

    contract = ContractCreate(
        employee_id=1,
        contract_type="Hợp đồng không xác định thời hạn",
        start_date=date(2026, 1, 1),
        status="active",
    )
    assert contract.contract_type == "Hợp đồng không xác định thời hạn"

    cert = CertificateCreate(
        employee_id=1,
        name="Chứng chỉ An toàn hóa chất",
        issuer="Cục Hóa chất",
        issued_date=date(2026, 3, 1),
    )
    assert cert.issuer == "Cục Hóa chất"


def test_hr_workflow_with_db(client):
    """Test HR CRUD workflow when database is active."""
    # 1. Create department
    dept_res = client.post("/api/v1/hr/departments", json={"code": "KCS_TEST", "name": "Bộ phận KCS Test"})
    assert dept_res.status_code in (200, 201), dept_res.text
    dept_id = dept_res.json()["id"]

    # 2. Create employee
    emp_res = client.post("/api/v1/hr/employees", json={
        "employee_code": "TEST-NV99",
        "full_name": "Trần Thị Test",
        "department_code": "KCS_TEST",
        "position": "Kỹ thuật viên",
        "status": "active",
    })
    assert emp_res.status_code in (200, 201), emp_res.text
    emp_id = emp_res.json()["id"]

    # 3. Check dashboard
    dash_res = client.get("/api/v1/hr/dashboard")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_employees"] >= 1

    # 4. Create attendance
    att_res = client.post("/api/v1/hr/attendance", json={
        "employee_id": emp_id,
        "work_date": str(date.today()),
        "status": "present",
    })
    assert att_res.status_code in (200, 201), att_res.text
    att_id = att_res.json()["id"]

    # 5. Create leave request & decide
    leave_res = client.post("/api/v1/hr/leave-requests", json={
        "employee_id": emp_id,
        "leave_type": "annual",
        "start_date": str(date.today()),
        "end_date": str(date.today()),
        "reason": "Việc gia đình",
    })
    assert leave_res.status_code in (200, 201), leave_res.text
    leave_id = leave_res.json()["id"]

    decide_res = client.patch(f"/api/v1/hr/leave-requests/{leave_id}/decision", json={"status": "approved"})
    assert decide_res.status_code == 200
    assert decide_res.json()["status"] == "approved"

    # Cleanup
    client.delete(f"/api/v1/hr/leave-requests/{leave_id}")
    client.delete(f"/api/v1/hr/attendance/{att_id}")
    client.delete(f"/api/v1/hr/employees/{emp_id}")
    client.delete(f"/api/v1/hr/departments/{dept_id}")
