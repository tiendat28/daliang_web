"""Quyen cua module Kho (warehouse)."""
from app.modules.auth.permissions import resource

PERMISSIONS = (
    resource("warehouse", "stock", "tồn kho theo lô", export=True)
    + resource("warehouse", "receipts", "phiếu nhập kho", export=True)
    + resource("warehouse", "dispatches", "phiếu xuất kho", export=True, approve=True)
    + resource("warehouse", "locations", "vị trí kho")
    + resource("warehouse", "audits", "phiếu kiểm kê", export=True)
)
