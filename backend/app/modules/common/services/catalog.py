"""Danh muc san pham cong ty - nap tu app/data/company_products.json.

Chay bang tay (vd sau khi sua file Excel va dung lai file JSON):
    docker compose exec backend python -m app.modules.common.services.catalog

Nap = thay ca danh muc: ma co trong file thi ghi de (giu nguyen id, nen moi
thu dang tro toi ma do van dung), ma khong co trong file thi xoa. Truoc khi xoa,
cac bang dang tro toi ma cu duoc chuyen sang ma goc trong danh muc moi
(NCZ-49A -> NCZ-49), khong co ma goc thi bo lien ket - chu da in tren phieu
(display_name, product_code_text) van giu nguyen.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Iterable, TypeVar

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.common import models

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "company_products.json"

# Thanh phan cua mot ma: NCZ-49A, 810B, TR-3B -> ma goc NCZ-49, 810, TR-3
_VARIANT_SUFFIX = re.compile(r"^(.*\d)[A-Z]{1,2}$")

T = TypeVar("T")


def normalize_code(code: str | None) -> str:
    return " ".join((code or "").split()).upper()


def resolve_code(code: str | None, known: dict[str, T]) -> T | None:
    """Tim ma trong `known` (khoa da normalize_code): trung khop, hoac ma goc cua thanh phan."""
    key = normalize_code(code)
    if not key:
        return None
    if key in known:
        return known[key]
    match = _VARIANT_SUFFIX.match(key)
    return known.get(match.group(1)) if match else None


def product_lookup(db: Session) -> dict[str, models.CompanyProduct]:
    return {normalize_code(p.code): p for p in db.query(models.CompanyProduct)}


def load_catalog() -> list[dict]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def build_modes(modes: Iterable[dict]) -> list[models.CompanyProductMode]:
    """Danh sach che do theo thu tu; che do khong co thong so nao thi bo."""
    return [
        models.CompanyProductMode(position=index, name=mode["name"], params=mode["params"])
        for index, mode in enumerate((m for m in modes if m["params"]), start=1)
    ]


def _apply(product: models.CompanyProduct, item: dict) -> None:
    for key in ("code", "name", "name_en", "category", "usage_stage", "materials", "description"):
        setattr(product, key, item.get(key))
    product.modes = build_modes(item.get("modes", []))


# Module khac tro toi san pham (vd lab: lay mau, luu trinh, quy trinh chuan)
# dang ky ham noi lai tham chieu o day, trong ham register() cua module do -
# common khong import bang cua module khac.
# Chu ky: hook(db, remap, count) - remap: id ma cu -> id ma moi (None = bo lien
# ket); count(new_id) de dem vao bao cao; tra ve so ban ghi phai xoa.
ProductRelinkHook = Callable[[Session, dict, Callable[[int | None], None]], int]
PRODUCT_RELINK_HOOKS: list[ProductRelinkHook] = []


def _relink_references(db: Session, remap: dict[int, int | None], summary: dict) -> None:
    """Chuyen moi tham chieu toi ma cu sang ma moi theo `remap` (None = bo lien ket)."""
    def count(new_id):
        summary["relinked" if new_id else "unlinked"] += 1

    for row in db.query(models.CustomerFieldProduct).filter(
        models.CustomerFieldProduct.company_product_id.in_(list(remap))
    ):
        row.company_product_id = remap[row.company_product_id]
        count(row.company_product_id)

    for hook in PRODUCT_RELINK_HOOKS:
        summary["samples_deleted"] += hook(db, remap, count)


def replace_catalog(db: Session) -> dict:
    """Thay danh muc bang file JSON va noi lai cac bang lien quan. Khong commit."""
    existing = product_lookup(db)
    kept: dict[str, models.CompanyProduct] = {}

    for item in load_catalog():
        key = normalize_code(item["code"])
        product = existing.pop(key, None)
        if product is None:
            product = models.CompanyProduct()
            db.add(product)
        _apply(product, item)
        kept[key] = product
    db.flush()

    # id ma cu -> id ma moi (None = khong con ma tuong ung)
    remap = {}
    for old in existing.values():
        target = resolve_code(old.code, kept)
        remap[old.id] = target.id if target else None

    summary = {"products": len(kept), "removed": len(remap), "relinked": 0, "unlinked": 0, "samples_deleted": 0}
    if remap:
        _relink_references(db, remap, summary)
        db.flush()
        for old in existing.values():
            db.delete(old)

    # Ma KH go tay truoc day chua khop san pham nao thi thu khop lai voi danh muc moi
    for row in db.query(models.CustomerFieldProduct).filter(
        models.CustomerFieldProduct.company_product_id.is_(None)
    ):
        target = resolve_code(row.product_code_text, kept)
        if target:
            row.company_product_id = target.id
            summary["relinked"] += 1

    db.flush()
    return summary


def main() -> None:
    from app.modules import load_all_modules
    load_all_modules()   # de cac module kip dang ky hook noi lai tham chieu
    with SessionLocal() as db:
        summary = replace_catalog(db)
        db.commit()
    print(
        f"Da nap {summary['products']} ma, xoa {summary['removed']} ma cu; "
        f"noi lai {summary['relinked']} lien ket, bo {summary['unlinked']} lien ket, "
        f"xoa {summary['samples_deleted']} ban ghi lay mau."
    )


if __name__ == "__main__":
    main()
