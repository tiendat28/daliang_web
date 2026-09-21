"""To phieu A4: dung trang, lap tieu de bang, ten file PDF."""
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

from app.services.test_process_sheet import (
    COMPACT_ROW_THRESHOLD,
    build_sheet_context,
    pdf_filename,
    render_sheet_html,
    render_sheet_pdf,
)
from tests.conftest import make_chemical, make_concentration, make_process, make_step

TABLE_HEADERS = ("STT", "HẠNG MỤC", "THỜI GIAN", "NHIỆT ĐỘ", "pH", "NỒNG ĐỘ", "HÓA CHẤT")


def steps_range(count: int):
    """count buoc giong nhau, du chi tiet de hang cao binh thuong."""
    return [
        make_step(
            i, f"Công đoạn {i}",
            time_min=1, time_max=2, time_unit="min",
            temp_mode="range", temp_min=20, temp_max=30,
            concentrations=[make_concentration(None, 10, None, "%")],
            chemicals=[make_chemical("CHB-60")],
        )
        for i in range(1, count + 1)
    ]


def pdf_pages(pdf: bytes) -> list[str]:
    """Chu tren tung trang cua file PDF."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sheet.pdf"
        path.write_bytes(pdf)
        count = int(re.search(
            r"Pages:\s+(\d+)",
            subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True).stdout,
        ).group(1))
        pages = []
        for page in range(1, count + 1):
            out = subprocess.run(
                ["pdftotext", "-f", str(page), "-l", str(page), str(path), "-"],
                capture_output=True, text=True, check=True,
            )
            pages.append(out.stdout)
        return pages


# ---------- Ngu canh truyen vao template ----------

def test_context_danh_lai_stt_lien_tuc():
    """position trong DB co the thua/thieu sau khi keo tha; in ra phai la 1..n."""
    steps = [make_step(5, "A"), make_step(9, "B"), make_step(2, "C")]
    context = build_sheet_context(make_process(steps), None, "file:///static")
    assert [s["position"] for s in context["steps"]] == [1, 2, 3]


def test_context_so_mau_va_thang():
    context = build_sheet_context(make_process([make_step(1, "A")]), None, "file:///static")
    assert context["sample_quantity"] == "02"
    assert context["test_month"] == "08/2026"


@pytest.mark.parametrize("count, compact", [(10, False), (12, False), (13, True), (16, True)])
def test_che_do_hang_thap_bat_tu_tren_12_buoc(count, compact):
    context = build_sheet_context(make_process(steps_range(count)), None, "file:///static")
    assert context["compact_rows"] is compact
    assert COMPACT_ROW_THRESHOLD == 12


# ---------- HTML ----------

def test_html_khong_cho_chen_the_qua_du_lieu_nhap():
    process = make_process([make_step(1, "<b>đậm</b>")], customer_name="<img src=x onerror=alert(1)>")
    html = render_sheet_html(process, None, screen=True)
    assert "<img src=x" not in html
    assert "&lt;img src=x" in html
    assert "<b>đậm</b>" not in html


def test_html_giu_chi_so_duoi():
    process = make_process([make_step(1, "Tẩy sáng", chemicals=[make_chemical("HNO_3")])])
    assert "HNO<sub>3</sub>" in render_sheet_html(process, None, screen=True)


def test_html_xem_truoc_dung_url_tuyet_doi_con_pdf_dung_file():
    process = make_process([make_step(1, "A")])
    assert "http" in render_sheet_html(process, None, screen=True)
    assert "file://" in render_sheet_html(process, None, screen=False)


# ---------- PDF ----------

def test_pdf_10_buoc_vua_1_trang():
    pages = pdf_pages(render_sheet_pdf(make_process(steps_range(10)), None))
    assert len(pages) == 1


def test_pdf_16_buoc_van_vua_1_trang():
    """Tren 12 buoc thi hang thap xuong 8mm de co vua 1 trang."""
    pages = pdf_pages(render_sheet_pdf(make_process(steps_range(16)), None))
    assert len(pages) == 1


def test_pdf_25_buoc_sang_trang_2_va_lap_tieu_de_bang():
    pages = pdf_pages(render_sheet_pdf(make_process(steps_range(25)), None))
    assert len(pages) == 2
    for header in TABLE_HEADERS:
        assert header in pages[0], f"trang 1 thieu cot {header}"
        assert header in pages[1], f"trang 2 khong lap lai cot {header}"


def test_pdf_25_buoc_khong_cat_doi_hang():
    """Moi buoc phai xuat hien dung 1 lan, tren dung 1 trang."""
    pages = pdf_pages(render_sheet_pdf(make_process(steps_range(25)), None))
    for index in range(1, 26):
        # Chan chu so phia sau de "Cong doan 2" khong khop voi "Cong doan 20"
        operation = re.compile(rf"Công đoạn {index}(?![0-9])")
        hits = [p for p, text in enumerate(pages) if operation.search(text)]
        assert len(hits) == 1, f"Công đoạn {index} nam tren {len(hits)} trang"


def test_pdf_khong_tach_nguoi_lap_khoi_ho_ten():
    pages = pdf_pages(render_sheet_pdf(make_process(steps_range(25)), None))
    for text in pages:
        if "Người lập" in text:
            assert "Vũ Thị Oanh" in text, "ho ten bi day sang trang khac"


def test_pdf_letterhead_chi_o_trang_1():
    pages = pdf_pages(render_sheet_pdf(make_process(steps_range(25)), None))
    assert "DALIANG CHEMICAL VIETNAM CO.,LTD" in pages[0]
    assert "DALIANG CHEMICAL VIETNAM CO.,LTD" not in pages[1]


def test_pdf_in_dung_noi_dung_cua_phieu_mau():
    steps = [
        make_step(1, "Tiền xử lí"),
        make_step(
            2, "Mạ kẽm kiềm",
            time_min=50, time_unit="min", temp_mode="range", temp_min=20, temp_max=30,
            concentrations=[
                make_concentration("Zn^2+", 8, 16, "g/l"),
                make_concentration("NaOH", 110, 160, "g/l"),
            ],
            chemicals=[make_chemical(c) for c in ("NCZ-48A", "NCZ-48B", "NCZ-48C", "NCZ-48R")],
        ),
        make_step(3, "Rửa nước", time_min=2, time_max=3, time_unit="min", temp_mode="ambient"),
    ]
    text = pdf_pages(render_sheet_pdf(make_process(steps), None))[0]
    for expected in ("LƯU TRÌNH TEST MẪU", "Nhà máy Z-113", "02", "08/2026",
                     "50 phút", "20-30°C", "2-3 phút", "Thường",
                     "NaOH: 110-160g/l", "NCZ-48R", "Vũ Thị Oanh"):
        assert expected in text, f"thieu {expected!r} tren phieu"
    assert "pH" in text and "PH" not in text.replace("pH", "")


def test_pdf_hien_duoc_chu_trung_khong_ra_o_vuong():
    text = pdf_pages(render_sheet_pdf(make_process([make_step(1, "A")]), None))[0]
    assert "越南大亮化工有限公司" in text
    assert "電話" in text


# ---------- Ten file ----------

@pytest.mark.parametrize("code, customer, expected", [
    ("LT-2026-001", "Nhà máy Z-113", "LT-2026-001_Nha-may-Z-113.pdf"),
    ("LT-2026-002", "Công ty TNHH Cơ khí Tiến Đạt", "LT-2026-002_Cong-ty-TNHH-Co-khi-Tien-Dat.pdf"),
    ("LT-2026-003", "", "LT-2026-003.pdf"),
])
def test_pdf_filename_bo_dau(code, customer, expected):
    assert pdf_filename({"code": code, "customer_name": customer}) == expected
