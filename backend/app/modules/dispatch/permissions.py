"""Quyen cua module Dieu phoi xe (dispatch)."""
from app.modules.auth.permissions import resource

PERMISSIONS = (
    resource("dispatch", "trips", "chuyến giao hàng", export=True, approve=True)
    + resource("dispatch", "vehicles", "xe giao hàng")
    + resource("dispatch", "drivers", "tài xế")
)
