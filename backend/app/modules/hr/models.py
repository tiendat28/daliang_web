"""Du lieu nhan su: ho so, cham cong, nghi phep, hop dong, chung chi."""
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base

SCHEMA = "hr"


class _InSchema:
    __table_args__ = {"schema": SCHEMA}


class Department(_InSchema, Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    code = Column(String(30), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    employees = relationship("EmployeeProfile", back_populates="department_record")


class EmployeeProfile(_InSchema, Base):
    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("employee_code", name="uq_hr_employees_code"),
        {"schema": SCHEMA},
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("auth.users.id", ondelete="SET NULL"), unique=True)
    employee_code = Column(String(20), nullable=False)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150))
    phone = Column(String(50))
    department_code = Column(String(30), ForeignKey("hr.departments.code", ondelete="SET NULL"))
    position = Column(String(120))
    start_date = Column(Date)
    contract_end = Column(Date)
    status = Column(String(30), nullable=False, default="active")
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    department_record = relationship("Department", back_populates="employees")
    user = relationship("User", foreign_keys=[user_id])
    attendance = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="employee", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="employee", cascade="all, delete-orphan")


class Attendance(_InSchema, Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("employee_id", "work_date", name="uq_hr_attendance_day"), {"schema": SCHEMA})

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("hr.employees.id", ondelete="CASCADE"), nullable=False)
    work_date = Column(Date, nullable=False)
    check_in = Column(Time)
    check_out = Column(Time)
    status = Column(String(30), nullable=False, default="present")
    note = Column(Text)

    employee = relationship("EmployeeProfile", back_populates="attendance")


class LeaveRequest(_InSchema, Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("hr.employees.id", ondelete="CASCADE"), nullable=False)
    leave_type = Column(String(50), nullable=False, default="annual")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)
    status = Column(String(30), nullable=False, default="pending")
    reviewed_by = Column(Integer, ForeignKey("auth.users.id", ondelete="SET NULL"))
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    employee = relationship("EmployeeProfile", back_populates="leave_requests")


class Contract(_InSchema, Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("hr.employees.id", ondelete="CASCADE"), nullable=False)
    contract_type = Column(String(80), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(String(30), nullable=False, default="active")
    note = Column(Text)

    employee = relationship("EmployeeProfile", back_populates="contracts")


class Certificate(_InSchema, Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("hr.employees.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(180), nullable=False)
    issuer = Column(String(150))
    issued_date = Column(Date)
    expires_at = Column(Date)
    note = Column(Text)

    employee = relationship("EmployeeProfile", back_populates="certificates")
