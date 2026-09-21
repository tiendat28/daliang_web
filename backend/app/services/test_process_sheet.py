"""Dung du lieu cho to phieu "Luu trinh test mau" va xuat PDF.

Chi co MOT template Jinja2 (templates/test_process_sheet.html) dung cho ca khung
xem truoc tren web lan file PDF, nen xem the nao in ra the ay. Khac nhau duy nhat
la `asset_base`: xuat PDF thi tro file:// vao thu muc static de WeasyPrint doc
thang tu dia, tra HTML cho iframe thi tro URL static cua API.
"""
from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.seed import COMPANY_PROFILE
from app.services.test_process_format import (
    field,
    format_sample_quantity,
    format_test_month,
    step_display,
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

# Tren nguong nay thi ha chieu cao toi thieu cua hang xuong 8mm de co vua 1 trang
COMPACT_ROW_THRESHOLD = 12

# Letterhead mac dinh khi bang company_profile chua co du lieu - dung chung mot
# ban voi seed de doi dia chi/so dien thoai chi phai sua o mot cho
DEFAULT_PROFILE = COMPANY_PROFILE
DEFAULT_LOGO_PATH = COMPANY_PROFILE["logo_path"]


_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)


def build_sheet_context(process: Any, profile: Any, asset_base: str) -> dict[str, Any]:
    """Gom moi thu can in ra phieu, da qua formatter."""
    steps = list(field(process, "steps") or [])
    return {
        "code": field(process, "code") or "",
        "customer_name": field(process, "customer_name") or "",
        "requirement": field(process, "requirement") or "",
        "sample_quantity": format_sample_quantity(field(process, "sample_quantity")),
        "test_month": format_test_month(field(process, "test_month")),
        "prepared_by": field(process, "prepared_by") or "",
        "profile": _profile_context(profile, asset_base),
        "compact_rows": len(steps) > COMPACT_ROW_THRESHOLD,
        "steps": [
            # position luu trong DB co the thua/thieu sau khi keo tha -> danh lai 1..n khi in
            {"position": index, **step_display(step)}
            for index, step in enumerate(steps, start=1)
        ],
    }


def render_sheet_html(process: Any, profile: Any, *, screen: bool) -> str:
    """HTML cua to phieu. screen=True cho iframe xem truoc, False cho WeasyPrint."""
    asset_base = _static_url_base() if screen else _static_file_base()
    context = build_sheet_context(process, profile, asset_base)
    template = _env.get_template("test_process_sheet.html")
    return template.render(sheet=context, asset_base=asset_base, screen=screen)


def render_sheet_pdf(process: Any, profile: Any) -> bytes:
    """File PDF cua to phieu."""
    from weasyprint import HTML  # import tai cho: keo theo pango/cairo, khong can khi chay test formatter

    html = render_sheet_html(process, profile, screen=False)
    return HTML(string=html, base_url=str(STATIC_DIR)).write_pdf()


def pdf_filename(process: Any) -> str:
    """"LT-2026-001_Nha-may-Z-113.pdf" - bo dau de dung duoc o moi he dieu hanh."""
    code = field(process, "code") or "luu-trinh"
    customer = _slugify(field(process, "customer_name") or "")
    return f"{code}_{customer}.pdf" if customer else f"{code}.pdf"


def _profile_context(profile: Any, asset_base: str) -> dict[str, Any]:
    data = {key: field(profile, key) or value for key, value in DEFAULT_PROFILE.items()}
    logo_path = data.get("logo_path") or DEFAULT_LOGO_PATH
    data["logo_url"] = f"{asset_base}/{logo_path.lstrip('/')}" if _logo_exists(logo_path) else ""
    return data


def _logo_exists(logo_path: str) -> bool:
    candidate = (STATIC_DIR / logo_path.lstrip("/")).resolve()
    # Chan ../ tro ra ngoai thu muc static
    return candidate.is_file() and str(candidate).startswith(str(STATIC_DIR.resolve()))


def _static_url_base() -> str:
    """URL static cua API - iframe dung srcdoc nen phai la duong dan tuyet doi."""
    return os.environ.get("STATIC_BASE_URL", "http://localhost:8001/api/static")


def _static_file_base() -> str:
    return STATIC_DIR.resolve().as_uri()


def _slugify(text: str) -> str:
    stripped = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in stripped if unicodedata.category(c) != "Mn")
    stripped = stripped.replace("Đ", "D").replace("đ", "d")
    stripped = re.sub(r"[^A-Za-z0-9]+", "-", stripped)
    return stripped.strip("-")

