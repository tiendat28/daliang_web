"""Schema API nhan su."""
from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from app.core.schemas import ORM_CONFIG


class DepartmentBase(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=120)
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    pass


class DepartmentOut(DepartmentBase):
    id: int
    model_config = ORM_CONFIG


class EmployeeBase(BaseModel):
    user_id: Optional[int] = None
    employee_code: str = Field(min_length=1, max_length=20)
    full_name: str = Field(min_length=1, max_length=150)
    email: Optional[str] = None
    phone: Optional[str] = None
    department_code: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[date] = None
    contract_end: Optional[date] = None
    status: str = "active"
    note: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    department_name: Optional[str] = None
    model_config = ORM_CONFIG


class AttendanceBase(BaseModel):
    employee_id: int
    work_date: date
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    status: str = "present"
    note: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(AttendanceBase):
    pass


class AttendanceOut(AttendanceBase):
    id: int
    employee_name: Optional[str] = None
    model_config = ORM_CONFIG


class LeaveRequestBase(BaseModel):
    employee_id: int
    leave_type: str = "annual"
    start_date: date
    end_date: date
    reason: Optional[str] = None

    @model_validator(mode="after")
    def valid_range(self):
        if self.end_date < self.start_date:
            raise ValueError("Ngày kết thúc phải sau hoặc bằng ngày bắt đầu")
        return self


class LeaveRequestCreate(LeaveRequestBase):
    pass


class LeaveRequestUpdate(LeaveRequestBase):
    pass


class LeaveRequestOut(LeaveRequestBase):
    id: int
    status: str
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    employee_name: Optional[str] = None
    model_config = ORM_CONFIG


class LeaveDecisionIn(BaseModel):
    status: str = Field(pattern="^(approved|rejected)$")


class ContractBase(BaseModel):
    employee_id: int
    contract_type: str = Field(min_length=1, max_length=80)
    start_date: date
    end_date: Optional[date] = None
    status: str = "active"
    note: Optional[str] = None


class ContractCreate(ContractBase):
    pass


class ContractUpdate(ContractBase):
    pass


class ContractOut(ContractBase):
    id: int
    employee_name: Optional[str] = None
    model_config = ORM_CONFIG


class CertificateBase(BaseModel):
    employee_id: int
    name: str = Field(min_length=1, max_length=180)
    issuer: Optional[str] = None
    issued_date: Optional[date] = None
    expires_at: Optional[date] = None
    note: Optional[str] = None


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(CertificateBase):
    pass


class CertificateOut(CertificateBase):
    id: int
    employee_name: Optional[str] = None
    model_config = ORM_CONFIG


class HrDashboardOut(BaseModel):
    total_employees: int
    active_employees: int
    present_today: int
    leave_today: int
    pending_leave_requests: int
    contracts_expiring: int
    certificates_expiring: int
    employees: List[EmployeeOut]
    pending_leaves: List[LeaveRequestOut]
    expiring_certificates: List[CertificateOut]
