"""Quy tac dinh dang khi in phieu "Luu trinh test mau" (muc 3 cua dac ta).

Moi ham tra ve chuoi HTML DA ESCAPE, co the chua <sub>/<sup> -> FE hien bang
v-html, template Jinja2 in bang |safe. Khong ham nao duoc tra ve HTML tho tu
du lieu nguoi dung nhap.
"""
from __future__ import annotations

import html
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

# In ra phieu bang tieng Viet, luu trong DB bang ma tieng Anh.
TIME_UNIT_LABELS = {"sec": "giây", "min": "phút", "hour": "giờ"}

AMBIENT_LABEL = "Thường"

def format_number(value: Any) -> str:
    """Bo so 0 thua: 50.00 -> "50", 1.30 -> "1.3". Dau thap phan la "." nhu mau."""
    if value is None or value == "":
        return ""
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return str(value)
    normalized = number.normalize()
    # normalize() doi 100 thanh 1E+2 -> quay ve dang thuong
    if normalized == normalized.to_integral_value():
        normalized = normalized.quantize(Decimal(1))
    return format(normalized, "f")


def format_range(value_min: Any, value_max: Any) -> str:
    """Co ca hai -> "min-max" (gach noi, khong dau cach). Chi 1 gia tri -> gia tri do."""
    low = format_number(value_min)
    high = format_number(value_max)
    if low and high:
        return low if low == high else f"{low}-{high}"
    return low or high


def apply_formula_markers(text: str) -> str:
    """Tu doi chu so trong cong thuc sang cu phap danh dau: HNO3 -> HNO_3, Zn2+ -> Zn^2+.

    Dung khi chon mot hoa chat PTN co cong thuc; ma san pham (NCZ-48A) khong doi
    vi chu so o do khong dung ngay sau chu cai.
    """
    if not text:
        return ""

    def replace(match: re.Match[str]) -> str:
        digits = match.group(1)
        is_charge = match.string[match.end():match.end() + 1] in ("+", "-")
        return f"{'^' if is_charge else '_'}{digits}"

    return re.sub(r"(?<=[A-Za-z)])(\d+)", replace, text)


def render_markers(text: str) -> str:
    """Escape HTML roi doi "_" thanh <sub> va "^" thanh <sup>.

    "HNO_3" -> "HNO<sub>3</sub>", "Zn^2+" -> "Zn<sup>2+</sup>".
    Dau danh dau an theo den het cum chu so (kem dau +/- neu la dien tich).
    """
    if not text:
        return ""
    escaped = html.escape(str(text))

    def wrap(match: re.Match[str]) -> str:
        tag = "sub" if match.group(1) == "_" else "sup"
        return f"<{tag}>{match.group(2)}</{tag}>"

    return re.sub(r"([_^])(\d+[+-]?|[+-])", wrap, escaped)


def format_time(step: Any) -> str:
    """"{khoang} {don vi}" -> "50 phút", "2-3 phút", "3-5 giây"."""
    override = field(step, "time_text")
    if override:
        return render_markers(override)
    span = format_range(field(step, "time_min"), field(step, "time_max"))
    if not span:
        return ""
    unit = TIME_UNIT_LABELS.get(field(step, "time_unit") or "", "")
    return html.escape(f"{span} {unit}".strip())


def format_temperature(step: Any) -> str:
    """ambient -> "Thường"; range -> "20-30°C"; none -> rong."""
    override = field(step, "temp_text")
    if override:
        return render_markers(override)
    mode = field(step, "temp_mode") or "none"
    if mode == "ambient":
        return html.escape(AMBIENT_LABEL)
    if mode != "range":
        return ""
    span = format_range(field(step, "temp_min"), field(step, "temp_max"))
    return html.escape(f"{span}°C") if span else ""


def format_ph(step: Any) -> str:
    """Chi la khoang, khong don vi: "1.3-1.8"."""
    override = field(step, "ph_text")
    if override:
        return render_markers(override)
    return html.escape(format_range(field(step, "ph_min"), field(step, "ph_max")))


def format_concentration(row: Any) -> str:
    """Co thanh phan -> "Zn²⁺: 8-16g/l"; khong co -> "0.5%"."""
    override = field(row, "text_override")
    if override:
        return render_markers(override)
    span = format_range(field(row, "value_min"), field(row, "value_max"))
    unit = field(row, "unit") or ""
    value = html.escape(f"{span}{unit}")
    component = field(row, "component")
    if not component:
        return value
    if not value:
        return render_markers(component)
    return f"{render_markers(component)}: {value}"


def format_chemical(row: Any) -> str:
    """Ten hoa chat nhu da chot luc chon, co dich chi so duoi/tren."""
    return render_markers(field(row, "display_name") or "")


def format_sample_quantity(quantity: Any) -> str:
    """In 2 chu so: 2 -> "02"."""
    try:
        return f"{int(quantity):02d}"
    except (TypeError, ValueError):
        return ""


def format_test_month(value: Any) -> str:
    """In "MM/YYYY": 2026-08-01 -> "08/2026"."""
    if value is None:
        return ""
    try:
        return f"{value.month:02d}/{value.year}"
    except AttributeError:
        return str(value)


def fold_accents(text: str) -> str:
    """Bo dau tieng Viet de so khop khong phan biet dau: "Rua nuoc" khop "Rửa nước"."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", str(text))
    folded = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return folded.replace("Đ", "D").replace("đ", "d")


def strip_markers(text: str) -> str:
    """Bo ky hieu _ ^ de lay chuoi tron cho danh sach / tim kiem: "HNO_3" -> "HNO3"."""
    if not text:
        return ""
    return re.sub(r"[_^]", "", str(text))


def step_display(step: Any) -> dict[str, Any]:
    """Toan bo phan chu in duoc cua 1 buoc, dung chung cho to A4 lan API chi tiet."""
    return {
        "operation": render_markers(field(step, "operation") or ""),
        "time": format_time(step),
        "temperature": format_temperature(step),
        "ph": format_ph(step),
        "concentrations": [format_concentration(c) for c in _iter(step, "concentrations")],
        "chemicals": [format_chemical(c) for c in _iter(step, "chemicals")],
    }


def field(obj: Any, name: str) -> Any:
    """Doc thuoc tinh tu ca model SQLAlchemy lan dict (dung cho /preview-sheet)."""
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _iter(obj: Any, name: str) -> Iterable[Any]:
    return field(obj, name) or []
