"""Doi file Excel tong hop san pham cong ty sang company_products.json.

Chay tren may dev (can openpyxl, backend khong can):
    python backend/app/data/build_company_products.py "San pham cong ty.xlsx"

File Excel: dong 1 la tieu de, dong 2 la ten cot, tu dong 3 moi dong la mot
"che do su dung" cua mot ma - ma co nhieu che do thi lap lai o nhieu dong.
Cot cuoi gop cac thong so bang " | ".

Sau khi doi xong, nap vao database bang:
    docker compose exec backend python -m app.core.product_catalog
"""
import json
import sys
from pathlib import Path

import openpyxl

OUT_PATH = Path(__file__).with_name("company_products.json")


def _clean(value):
    text = " ".join(str(value).split()) if value is not None else ""
    return text or None


def build(xlsx_path: str) -> list[dict]:
    sheet = openpyxl.load_workbook(xlsx_path, read_only=True).active
    products: dict[str, dict] = {}
    for row in sheet.iter_rows(min_row=3, values_only=True):
        code = _clean(row[0])
        if not code:
            continue
        product = products.setdefault(code, {
            "code": code,
            "name": _clean(row[2]) or code,
            "name_en": _clean(row[1]),
            "category": _clean(row[3]),
            "usage_stage": _clean(row[4]),
            "materials": _clean(row[5]),
            "description": _clean(row[6]),
            "modes": [],
        })
        params = [p for p in (_clean(part) for part in str(row[8] or "").split(" | ")) if p]
        product["modes"].append({"name": _clean(row[7]) or "Chung", "params": params})
    return list(products.values())


if __name__ == "__main__":
    catalog = build(sys.argv[1])
    OUT_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(catalog)} ma, {sum(len(p['modes']) for p in catalog)} che do -> {OUT_PATH}")
