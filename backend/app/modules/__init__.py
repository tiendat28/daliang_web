"""Danh sach module cua he thong - khop 1-1 voi apps/portal/src/modules.

Moi module la mot thu muc cung cau truc:
    models.py    bang DB, nam trong schema Postgres trung ten module
    schemas.py   du lieu vao/ra (Pydantic)
    service.py   nghiep vu (module lon thi tach thu muc services/)
    router.py    `router` cua module, gan duoi /api/v1/<module>
    permissions.py  PERMISSIONS = [(ma quyen, mo ta)] - xem auth/permissions.py
                 (module nhieu nhom thi tach routers/, router.py gom lai)

Them bo phan moi: tao thu muc cung khung roi them ten vao MODULES.
"""
import importlib

# common: du lieu dung chung; auth: tai khoan/quyen; system: quan tri + nhat ky
MODULES = ["common", "auth", "system", "lab", "hr", "accounting", "warehouse", "dispatch", "website"]


def load_all_modules() -> None:
    """Nap model cua moi module (de SQLAlchemy/Alembic thay du bang) va noi
    cac module voi nhau. Goi mot lan luc khoi dong va o dau moi lenh chay tay."""
    for name in MODULES:
        importlib.import_module(f"app.modules.{name}.models")

    # Nap lai danh muc san pham (common) phai noi lai ca bang cua lab dang tro toi
    from app.modules.common.services.catalog import PRODUCT_RELINK_HOOKS
    from app.modules.lab.services.product_links import relink_product_references
    if relink_product_references not in PRODUCT_RELINK_HOOKS:
        PRODUCT_RELINK_HOOKS.append(relink_product_references)


def module_routers():
    """`router` cua tung module, theo thu tu MODULES."""
    return [importlib.import_module(f"app.modules.{name}.router").router for name in MODULES]
