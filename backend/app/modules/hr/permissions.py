"""Quyen cua module nhan su."""
from app.modules.auth.permissions import resource

PERMISSIONS = [
    *resource("hr", "employees", "hồ sơ nhân viên", export=True),
    *resource("hr", "attendance", "chấm công", export=True),
    *resource("hr", "leave_requests", "đơn nghỉ phép", approve=True),
    *resource("hr", "contracts", "hợp đồng", export=True),
    *resource("hr", "certificates", "chứng chỉ", export=True),
    *resource("hr", "departments", "phòng ban"),
]
