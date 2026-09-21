"""Quy tac dinh dang khi in phieu (muc 3 cua dac ta)."""
from datetime import date

import pytest

from app.services.test_process_format import (
    apply_formula_markers,
    format_chemical,
    format_concentration,
    format_number,
    format_ph,
    format_range,
    format_sample_quantity,
    format_temperature,
    format_test_month,
    format_time,
    render_markers,
    step_display,
    strip_markers,
)
from tests.conftest import make_concentration, make_step


# ---------- So va khoang ----------

@pytest.mark.parametrize("value, expected", [
    (50.00, "50"),
    (1.30, "1.3"),
    (0.5, "0.5"),
    (100, "100"),
    (0, "0"),
    ("8", "8"),
    (None, ""),
    ("", ""),
])
def test_format_number_bo_so_0_thua(value, expected):
    assert format_number(value) == expected


@pytest.mark.parametrize("low, high, expected", [
    (8, 16, "8-16"),          # co ca hai -> gach noi, khong dau cach
    (50, None, "50"),         # chi co gia tri dau
    (None, 30, "30"),         # chi co gia tri cuoi
    (1, 1, "1"),              # bang nhau -> in 1 lan, khong ra "1-1"
    (1.30, 1.80, "1.3-1.8"),
    (None, None, ""),
])
def test_format_range(low, high, expected):
    assert format_range(low, high) == expected


# ---------- Thoi gian ----------

@pytest.mark.parametrize("kwargs, expected", [
    ({"time_min": 50, "time_unit": "min"}, "50 phút"),
    ({"time_min": 2, "time_max": 3, "time_unit": "min"}, "2-3 phút"),
    ({"time_min": 3, "time_max": 5, "time_unit": "sec"}, "3-5 giây"),
    ({"time_min": 2, "time_unit": "hour"}, "2 giờ"),
    ({}, ""),
    ({"time_min": 5}, "5"),                      # thieu don vi thi chi in so
    ({"time_text": "qua đêm"}, "qua đêm"),       # chu in thay the
    ({"time_min": 50, "time_unit": "min", "time_text": "đến khi hết bọt"}, "đến khi hết bọt"),
])
def test_format_time(kwargs, expected):
    assert format_time(make_step(1, "x", **kwargs)) == expected


# ---------- Nhiet do ----------

@pytest.mark.parametrize("kwargs, expected", [
    ({"temp_mode": "ambient"}, "Thường"),
    ({"temp_mode": "range", "temp_min": 20, "temp_max": 30}, "20-30°C"),
    ({"temp_mode": "range", "temp_min": 80, "temp_max": 100}, "80-100°C"),
    ({"temp_mode": "none"}, ""),
    # con so cu nhung mode = none thi van de trong
    ({"temp_mode": "none", "temp_min": 20, "temp_max": 30}, ""),
    ({"temp_mode": "range", "temp_text": "sôi"}, "sôi"),
])
def test_format_temperature(kwargs, expected):
    assert format_temperature(make_step(1, "x", **kwargs)) == expected


# ---------- pH ----------

@pytest.mark.parametrize("kwargs, expected", [
    ({"ph_min": 1.30, "ph_max": 1.80}, "1.3-1.8"),
    ({"ph_min": 7}, "7"),
    ({}, ""),
    ({"ph_text": "trung tính"}, "trung tính"),
])
def test_format_ph(kwargs, expected):
    assert format_ph(make_step(1, "x", **kwargs)) == expected


# ---------- Nong do ----------

def test_format_concentration_co_thanh_phan():
    row = make_concentration("NaOH", 110, 160, "g/l")
    assert format_concentration(row) == "NaOH: 110-160g/l"


def test_format_concentration_khong_co_thanh_phan():
    assert format_concentration(make_concentration(None, 0.5, None, "%")) == "0.5%"
    assert format_concentration(make_concentration(None, 10, None, "%")) == "10%"


def test_format_concentration_thanh_phan_co_chi_so():
    row = make_concentration("Zn^2+", 8, 16, "g/l")
    assert format_concentration(row) == "Zn<sup>2+</sup>: 8-16g/l"


def test_format_concentration_chu_in_thay_the():
    row = make_concentration("NaOH", 110, 160, "g/l", text_override="bão hòa")
    assert format_concentration(row) == "bão hòa"


# ---------- Chi so duoi / tren ----------

@pytest.mark.parametrize("raw, expected", [
    ("HNO3", "HNO_3"),
    ("H2SO4", "H_2SO_4"),
    ("Zn2+", "Zn^2+"),
    ("Ca(OH)2", "Ca(OH)_2"),
    # Ma san pham: chu so di sau dau "-" nen khong bi doi
    ("NCZ-48A", "NCZ-48A"),
    ("CHB-60", "CHB-60"),
    ("CR-3GD", "CR-3GD"),
    ("", ""),
])
def test_apply_formula_markers(raw, expected):
    assert apply_formula_markers(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("HNO_3", "HNO<sub>3</sub>"),
    ("Zn^2+", "Zn<sup>2+</sup>"),
    ("H_2SO_4", "H<sub>2</sub>SO<sub>4</sub>"),
    ("NCZ-48A", "NCZ-48A"),
    ("", ""),
])
def test_render_markers(raw, expected):
    assert render_markers(raw) == expected


def test_render_markers_escape_html_truoc_khi_danh_dau():
    """Chu nguoi dung nhap khong duoc tro thanh the HTML that."""
    assert render_markers("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert render_markers("a & b") == "a &amp; b"


def test_format_chemical_dich_chi_so():
    assert format_chemical({"display_name": "HNO_3"}) == "HNO<sub>3</sub>"
    assert format_chemical({"display_name": "NCZ-48A"}) == "NCZ-48A"


@pytest.mark.parametrize("raw, expected", [
    ("HNO_3", "HNO3"),
    ("Zn^2+", "Zn2+"),
    ("NCZ-48A", "NCZ-48A"),
])
def test_strip_markers(raw, expected):
    assert strip_markers(raw) == expected


# ---------- So luong mau va thang test ----------

@pytest.mark.parametrize("value, expected", [(2, "02"), (10, "10"), (1, "01"), (None, "")])
def test_format_sample_quantity_2_chu_so(value, expected):
    assert format_sample_quantity(value) == expected


def test_format_test_month():
    assert format_test_month(date(2026, 8, 1)) == "08/2026"
    assert format_test_month(date(2026, 12, 1)) == "12/2026"
    assert format_test_month(None) == ""


# ---------- Ca buoc ----------

def test_step_display_buoc_ma_kem_kiem(sample_steps):
    display = step_display(sample_steps[0])
    assert display["operation"] == "Mạ kẽm kiềm"
    assert display["time"] == "50 phút"
    assert display["temperature"] == "20-30°C"
    assert display["ph"] == ""
    assert display["concentrations"] == ["Zn<sup>2+</sup>: 8-16g/l", "NaOH: 110-160g/l"]
    assert display["chemicals"] == ["NCZ-48A", "NCZ-48B", "NCZ-48C", "NCZ-48R"]


def test_step_display_buoc_tay_sang(sample_steps):
    display = step_display(sample_steps[1])
    assert display["time"] == "3-5 giây"
    assert display["temperature"] == ""
    assert display["concentrations"] == ["0.5%"]
    assert display["chemicals"] == ["HNO<sub>3</sub>"]


def test_step_display_buoc_trong():
    """Buoc "Tien xu li" chi co ten, moi o con lai de trong."""
    display = step_display(make_step(1, "Tiền xử lí"))
    assert display["operation"] == "Tiền xử lí"
    assert display["time"] == display["temperature"] == display["ph"] == ""
    assert display["concentrations"] == display["chemicals"] == []
