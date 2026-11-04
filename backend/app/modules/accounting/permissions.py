"""Quyen cua module ke toan."""
from app.modules.auth.permissions import resource

PERMISSIONS = [
    *resource("accounting", "invoices", "hoá đơn", export=True),
    *resource("accounting", "vouchers", "phiếu thu chi", export=True),
    *resource("accounting", "receivables", "công nợ phải thu", export=True),
    *resource("accounting", "payables", "công nợ phải trả", export=True),
    *resource("accounting", "cashbook", "sổ quỹ", export=True),
    *resource("accounting", "reports", "báo cáo tài chính kế toán", export=True),
]
