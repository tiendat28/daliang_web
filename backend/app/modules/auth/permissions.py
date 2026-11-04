"""Quyen va vai tro mac dinh.

Moi module khai quyen cua minh trong `<module>/permissions.py` (bien PERMISSIONS,
danh sach (ma, mo ta)). Luc khoi dong, sync_permissions() gom tat ca vao bang
auth.permissions; tao vai tro mac dinh neu bang roles con trong.

Sau hanh dong (cot cua bang phan quyen): view (xem), create (them), update (sua),
delete (xoa), approve (duyet), export (xuat file). guard() tu map GET -> view,
POST -> create, PUT/PATCH -> update, DELETE -> delete. Rieng le thi dat ten rieng
(vd `system.users.manage`).
"""
import importlib

from sqlalchemy.orm import Session

from app.modules.auth import models

ALL = "*"   # vai tro giu quyen nay co moi quyen, ke ca quyen them ve sau


ACTIONS = {
    "view": "Xem", "create": "Thêm", "update": "Sửa", "delete": "Xoá",
    "approve": "Duyệt", "export": "Xuất file",
}


def resource(module: str, obj: str, label: str, *, export: bool = False, approve: bool = False) -> list[tuple[str, str]]:
    """Quyen cho mot chuc nang - vd resource("lab", "equipment", "thiết bị", export=True)
    -> lab.equipment.view / .create / .update / .delete / .export."""
    actions = ["view", "create", "update", "delete"] + (["approve"] if approve else []) + (["export"] if export else [])
    return [(f"{module}.{obj}.{action}", f"{ACTIONS[action]} {label}") for action in actions]


def collect_permissions() -> list[tuple[str, str]]:
    from app.modules import MODULES
    result = []
    for name in MODULES:
        try:
            module = importlib.import_module(f"app.modules.{name}.permissions")
        except ModuleNotFoundError:   # module chua khai quyen nao
            continue
        result += getattr(module, "PERMISSIONS", [])
    return result


def _codes(prefix: str, actions=tuple(ACTIONS)) -> list[str]:
    return [code for code, _ in collect_permissions() if code.startswith(prefix) and code.rsplit(".", 1)[1] in actions]


def default_roles() -> list[dict]:
    """Vai tro theo so do cong noi bo. Chi dung de tao lan dau - sau do sua o /system/roles."""
    common_view = _codes("common.", ("view",))
    return [
        {"code": "admin", "name": "Admin cao nhất", "require_2fa": True, "permissions": [ALL],
         "description": "Toàn quyền, quản lý tài khoản và phân quyền."},
        {"code": "lab", "name": "Kỹ thuật", "require_2fa": False,
         "permissions": _codes("lab.") + _codes("common.customers.") + _codes("common.products.")
                        + _codes("common.documents.") + ["common.company_profile.view"]
                        + _codes("website.contact_leads."),
         "description": "Phòng thí nghiệm, khách hàng, sản phẩm, tài liệu, đơn khách gửi từ web."},
        {"code": "warehouse", "name": "Kho", "require_2fa": False,
         "permissions": _codes("warehouse.") + common_view,
         "description": "Tồn kho theo lô, phiếu nhập/xuất, kiểm kê, vị trí kho."},
        {"code": "dispatch", "name": "Điều phối", "require_2fa": False,
         "permissions": _codes("dispatch.") + ["common.customers.view", "common.company_profile.view"],
         "description": "Bảng điều phối xe, chuyến giao hàng, quản lý xe và tài xế."},
        {"code": "driver", "name": "Tài xế", "require_2fa": False, "permissions": [],
         "description": "App tài xế trên điện thoại."},
        {"code": "accounting", "name": "Kế toán", "require_2fa": True,
         "permissions": _codes("accounting.") + ["common.customers.view", "common.products.view", "common.company_profile.view"],
         "description": "Hoá đơn, công nợ, sổ quỹ."},
        {"code": "hr", "name": "Nhân sự", "require_2fa": False,
         "permissions": _codes("hr.") + ["common.company_profile.view"],
         "description": "Nhân viên, chấm công, nghỉ phép, hợp đồng."},
    ]


def sync_permissions(db: Session) -> None:
    """Dua danh sach quyen trong code vao DB; tao vai tro mac dinh neu chua co vai tro nao."""
    declared = dict(collect_permissions())
    declared[ALL] = "Toàn quyền"
    existing = {p.code: p for p in db.query(models.Permission)}
    for code, description in declared.items():
        module = "all" if code == ALL else code.split(".", 1)[0]
        if code in existing:
            existing[code].description = description
        else:
            db.add(models.Permission(code=code, module=module, description=description))
    granted = {code for (code,) in db.query(models.role_permissions.c.permission_code).distinct()}
    for code, permission in existing.items():
        # Quyen da bo khoi code: chi xoa khi khong vai tro nao con giu. Quyen dang duoc
        # gan thi de migration chuyen doi (vd .edit -> .create/.update/.delete) - neu
        # xoa o day truoc khi migration chay, vai tro mat quyen ma khong ai hay.
        if code not in declared and code not in granted:
            db.delete(permission)
    db.flush()

    if db.query(models.Role).first():
        return
    permissions = {p.code: p for p in db.query(models.Permission)}
    for spec in default_roles():
        db.add(models.Role(
            code=spec["code"], name=spec["name"], description=spec["description"],
            require_2fa=spec["require_2fa"], is_system=True,
            permissions=[permissions[c] for c in dict.fromkeys(spec["permissions"]) if c in permissions],
        ))
    db.flush()
