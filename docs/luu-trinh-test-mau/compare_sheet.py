"""Doi chieu ban in voi mau giay `mau-goc.png`.

Chay trong container backend (co WeasyPrint + poppler + Pillow):

    docker compose exec -T backend python /app/../docs/luu-trinh-test-mau/compare_sheet.py

Sinh ra trong thu muc dich:
  - ban-in.pdf        file PDF cua luu trinh
  - ban-in.png        trang 1, scale dung bang mau giay (1154 x 1633)
  - so-sanh.png       mau giay | ban in, dat canh nhau
  - chong-lop.png     chong 2 anh len nhau (mau do = mau giay, xanh = ban in)
va in ra toa do cac moc chinh de chinh so mm trong template.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/app")

from PIL import Image  # noqa: E402

REF_WIDTH, REF_HEIGHT = 1154, 1633
PX_PER_MM = REF_WIDTH / 210.0

DOCS_DIR = Path(__file__).resolve().parent
OUT_DIR = DOCS_DIR / "_compare"   # .gitignore - anh sinh ra de doi chieu


def render(process_id: int) -> Path:
    from app.api.test_processes import get_company_profile, get_process_or_404
    from app.core.database import SessionLocal
    from app.services.test_process_sheet import render_sheet_pdf

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT_DIR / "ban-in.pdf"
    with SessionLocal() as db:
        process = get_process_or_404(db, process_id)
        pdf_path.write_bytes(render_sheet_pdf(process, get_company_profile(db)))
    return pdf_path


def page_count(pdf_path: Path) -> int:
    info = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
    for line in info.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 0


def to_png(pdf_path: Path) -> Image.Image:
    subprocess.run(
        ["pdftoppm", "-png", "-scale-to-x", str(REF_WIDTH), "-scale-to-y", str(REF_HEIGHT),
         "-f", "1", "-l", "1", str(pdf_path), str(OUT_DIR / "page")],
        check=True,
    )
    image = Image.open(OUT_DIR / "page-1.png").convert("RGB")
    image.save(OUT_DIR / "ban-in.png")
    return image


def side_by_side(reference: Image.Image, rendered: Image.Image) -> None:
    gap = 24
    canvas = Image.new("RGB", (reference.width + gap + rendered.width, REF_HEIGHT), "#d8dede")
    canvas.paste(reference, (0, 0))
    canvas.paste(rendered, (reference.width + gap, 0))
    canvas.save(OUT_DIR / "so-sanh.png")


def overlay(reference: Image.Image, rendered: Image.Image) -> None:
    """Mau giay vao kenh do, ban in vao kenh xanh -> lech cho nao thay ngay cho do."""
    ref_gray = reference.convert("L")
    out_gray = rendered.convert("L")
    canvas = Image.merge("RGB", (ref_gray, out_gray, out_gray))
    canvas.save(OUT_DIR / "chong-lop.png")


def ink_rows(image: Image.Image, threshold: int = 160) -> list[int]:
    """Chi so dong pixel co muc - dung de do vi tri theo chieu doc."""
    gray = image.convert("L")
    pixels = gray.load()
    rows = []
    for y in range(gray.height):
        for x in range(gray.width):
            if pixels[x, y] < threshold:
                rows.append(y)
                break
    return rows


def bands(rows: list[int], gap: int = 6) -> list[tuple[int, int]]:
    """Gom cac dong co muc lien nhau thanh tung dai."""
    if not rows:
        return []
    result = [[rows[0], rows[0]]]
    for y in rows[1:]:
        if y - result[-1][1] <= gap:
            result[-1][1] = y
        else:
            result.append([y, y])
    return [(a, b) for a, b in result]


def report(reference: Image.Image, rendered: Image.Image) -> None:
    print(f"{'dai muc (mm tu mep tren)':<34}{'MAU GIAY':<22}{'BAN IN'}")
    ref_bands = bands(ink_rows(reference))
    out_bands = bands(ink_rows(rendered))
    for index in range(max(len(ref_bands), len(out_bands))):
        left = f"{ref_bands[index][0] / PX_PER_MM:6.1f} - {ref_bands[index][1] / PX_PER_MM:6.1f}" if index < len(ref_bands) else " " * 15
        right = f"{out_bands[index][0] / PX_PER_MM:6.1f} - {out_bands[index][1] / PX_PER_MM:6.1f}" if index < len(out_bands) else ""
        print(f"  dai {index:<28}{left:<22}{right}")


def main() -> None:
    process_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    pdf_path = render(process_id)
    pages = page_count(pdf_path)
    print(f"So trang: {pages}")

    rendered = to_png(pdf_path)
    reference = Image.open(DOCS_DIR / "mau-goc.png").convert("RGB").resize((REF_WIDTH, REF_HEIGHT))
    side_by_side(reference, rendered)
    overlay(reference, rendered)
    report(reference, rendered)
    print(f"\nAnh nam o {OUT_DIR}")


if __name__ == "__main__":
    main()
