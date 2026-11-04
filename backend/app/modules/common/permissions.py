"""Quyen tren du lieu dung chung - xem app/modules/auth/permissions.py."""
from app.modules.auth.permissions import resource

PERMISSIONS = [
    *resource("common", "customers", "khách hàng", export=True),
    *resource("common", "products", "sản phẩm công ty (cả phần hiện trên website)", export=True),
    *resource("common", "documents", "tài liệu"),
    ("common.company_profile.view", "Xem thông tin công ty"),
    ("common.company_profile.update", "Sửa thông tin công ty"),
]
