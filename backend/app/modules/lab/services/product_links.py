"""Noi lai tham chieu san pham cua module lab khi nap lai danh muc (common.catalog)."""
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.modules.lab import models


def relink_product_references(db: Session, remap: dict, count) -> int:
    """Chuyen cac bang lab dang tro toi ma cu sang ma moi. Tra ve so ban ghi lay mau bi xoa."""
    old_ids = list(remap)
    deleted = 0

    for row in db.query(models.TestProcessStepChemical).filter(
        models.TestProcessStepChemical.product_id.in_(old_ids)
    ):
        row.product_id = remap[row.product_id]
        count(row.product_id)

    # company_product_id bat buoc: khong con san pham tuong ung thi ban ghi lay mau mat nghia
    for row in db.query(models.ChemicalSampling).filter(
        models.ChemicalSampling.company_product_id.in_(old_ids)
    ):
        if remap[row.company_product_id]:
            row.company_product_id = remap[row.company_product_id]
            count(row.company_product_id)
        else:
            db.delete(row)
            deleted += 1

    for template in db.query(models.ProcessTemplate):
        changed = False
        for step in template.steps or []:
            for chemical in step.get("chemicals", []):
                if chemical.get("product_id") in remap:
                    chemical["product_id"] = remap[chemical["product_id"]]
                    count(chemical["product_id"])
                    changed = True
        if changed:
            flag_modified(template, "steps")
    return deleted
