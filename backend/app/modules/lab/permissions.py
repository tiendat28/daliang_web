"""Quyen cua module ky thuat - xem app/modules/auth/permissions.py.
export: nut Xuat Excel / PDF va phan xuat du lieu trong bang Cai dat."""
from app.modules.auth.permissions import resource

PERMISSIONS = [
    *resource("lab", "chemicals", "hoá chất phòng thí nghiệm", export=True),
    *resource("lab", "indicators", "chất chỉ thị", export=True),
    *resource("lab", "equipment", "thiết bị", export=True),
    *resource("lab", "formulations", "đơn hàng HCTN", export=True),
    *resource("lab", "samples", "lấy mẫu hoá chất", export=True),
    *resource("lab", "analysis_reports", "báo cáo phân tích", export=True),
    *resource("lab", "work_logs", "nhật ký công tác", export=True),
    *resource("lab", "test_processes", "lưu trình test mẫu", export=True),
    *resource("lab", "process_templates", "quy trình chuẩn"),
]
