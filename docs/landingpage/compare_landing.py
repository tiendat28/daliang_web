"""Doi chieu trang chu cua website voi ban thiet ke goc `landingpage-goc.html`.

Cung vai tro nhu `docs/luu-trinh-test-mau/compare_sheet.py` lam voi to A4: day
la thuoc do duy nhat cho cau "giong het ban goc".

Chay tren may (khong chay trong container - can trinh duyet cua Playwright):

    python docs/landingpage/compare_landing.py

Truoc do: `docker compose -f infra/docker-compose.yml up -d` (can landing o :5174, backend o :8001).
Lan dau can cai:  pip install playwright pillow  &&  playwright install chromium

Sinh ra trong docs/landingpage/_compare/ (da .gitignore):
  goc-<W>.png / web-<W>.png   anh hai ban, cung be rong
  lech-<W>.png                cho nao khac thi to do
va in ty le diem anh lech + so phan tu trung khop toa do.

BA CHO PHAI LAM BANG NHAU TRUOC KHI DO, khong thi con so vo nghia:
  1. Noi dung: ban goc doc tu bien COMPANY/PRODUCTS trong file, ban web doc tu
     DB. Script nhoi du lieu that cua DB vao ban goc.
  2. Chu ban web da viet lai: doan gioi thieu cong ty (ban goc de trong) va
     dong cho ban do -> lay thang chu cua ban web dap vao ban goc.
  3. Font: ban goc goi Be Vietnam Pro tu Google Fonts, ban web dung file trong
     repo. Hai ban cung mot font nhung khac file thi chu ren canh khac nhau,
     lech gia ~0.5% diem anh ma khong sai mot ly nao ve bo cuc. Script chan
     Google Fonts va nap dung @font-face cua apps/landing/src/styles/site.css.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

DOCS_DIR = Path(__file__).resolve().parent
REPO = DOCS_DIR.parent.parent
OUT_DIR = DOCS_DIR / "_compare"
REFERENCE = DOCS_DIR / "landingpage-goc.html"
SITE_CSS = REPO / "apps" / "landing" / "src" / "styles" / "site.css"

SITE_ORIGIN = "http://localhost:5174"
SITE_URL = SITE_ORIGIN + "/"
# Dia chi gia, chi ton tai trong phien Playwright - de ban goc chay cung goc
# voi ban web thi /fonts/... trong repo moi tai duoc.
REFERENCE_URL = SITE_ORIGIN + "/__landingpage-goc.html"
API_URL = "http://localhost:8001/api/v1/website/public/site"

# Ba kho man hinh dung voi ba moc @media cua ban thiet ke
WIDTHS = [(1440, "may ban"), (1024, "may bang"), (390, "dien thoai")]

# Cho vai diem anh lech vi chu ren canh (anti-aliasing) khac nhau chut
TOLERANCE = 8

# Cac phan tu do toa do + kich thuoc, phu kin tung muc cua trang
SELECTORS = [
    ".nav", ".brand-text b", ".brand-text span", ".menu", ".menu a", ".nav-right", ".lang",
    ".nav-right .btn-sm", ".hero", ".hero-copy", ".hero-visual", ".hero h1", ".hero p", ".eyebrow",
    ".steps", ".about", ".about .ph", ".value", ".products-head", ".filters", ".filters button",
    ".grid3", ".pcard", ".pcard h3", ".pcard-links", ".certs", ".certs-side", ".lookup",
    ".lookup input", ".docs", ".doc", ".grid4", ".svc", ".contact", ".contact-form", "form",
    ".field", "form .btn", ".map", ".info", ".info>div", "footer", ".foot", ".foot p",
    ".foot-col", ".copy",
]

RECT_JS = """(sels) => sels.map(sel => {
  const el = document.querySelector(sel);
  if (!el) return [sel, null];
  const r = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  const round = v => Math.round(v * 100) / 100;
  // Bo qua toa do y tuyet doi: chi can x/rong/cao trung la bo cuc trung.
  return [sel, [round(r.x), round(r.width), round(r.height), cs.fontWeight, cs.fontSize, cs.color]];
})"""


def font_faces() -> str:
    """Lay nguyen cac khoi @font-face cua website - de ban goc dung dung file font do."""
    css = SITE_CSS.read_text(encoding="utf-8")
    return "\n".join(re.findall(r"@font-face\s*\{[^}]*\}", css))


def load_db_content() -> dict:
    with urllib.request.urlopen(API_URL, timeout=10) as response:
        return json.load(response)


def patch_script(data: dict, web_texts: dict, faces: str):
    """JS chay tren ban goc: nap font cua repo + du lieu that roi ve lai.

    web_texts: chu ma ban web da viet lai so voi ban goc (doan gioi thieu, dong
    cho ban do) - lay thang tu trang web dap vao ban goc.
    Giay to: DB chua co file "Chung nhan" thi web hien dung bon the cho cua ban
    goc, nen giu nguyen DOCS cua ban goc.
    """
    company = data["company"]
    products = [
        {"code": p["code"], "group": p["group"], "name": p["name"], "desc": p["desc"], "msds": "#", "tds": "#"}
        for p in data["products"]
    ]
    company_js = {
        "name": company["name"]["vi"], "address": company["address"]["vi"], "taxId": company["tax_id"],
        "phone": company["phone"], "email": company["email"],
        "hours": company["hours"], "mapQuery": company["map_query"] or "",
    }
    return """([faces, texts, company, products]) => {
        const tag = document.createElement('style');
        tag.textContent = faces;
        document.head.appendChild(tag);
        Object.values(I18N).forEach(table => Object.assign(table, texts));
        Object.assign(COMPANY, company);
        PRODUCTS.length = 0; PRODUCTS.push(...products);
        applyLang(lang);
    }""", [faces, web_texts, company_js, products]


def prepare(page):
    """Ban goc duoc phuc vu ngay tren goc cua Vite, va chan Google Fonts."""
    html = REFERENCE.read_text(encoding="utf-8")
    page.route(REFERENCE_URL, lambda route: route.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=html))
    page.route("**fonts.googleapis.com**", lambda route: route.abort())
    page.route("**fonts.gstatic.com**", lambda route: route.abort())


def shoot(page, url, width, patch=None):
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(url, wait_until="networkidle")
    if patch:
        page.evaluate(*patch)
    page.wait_for_timeout(700)
    return page.screenshot(full_page=True)


def compare_images(path_a: Path, path_b: Path, out: Path) -> tuple[float, int, int]:
    a = Image.open(path_a).convert("RGB")
    b = Image.open(path_b).convert("RGB")
    height = min(a.height, b.height)
    box = (0, 0, a.width, height)
    a_crop, b_crop = a.crop(box), b.crop(box)

    diff = ImageChops.difference(a_crop, b_crop).convert("L").point(lambda v: 255 if v > TOLERANCE else 0)
    marked = a_crop.copy()
    marked.paste(Image.new("RGB", a_crop.size, (255, 0, 0)), mask=diff)
    marked.save(out)

    changed = sum(diff.histogram()[255:])
    return changed / (a.width * height) * 100, a.height, b.height


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    data = load_db_content()
    faces = font_faces()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(device_scale_factor=1)
        prepare(page)

        page.set_viewport_size({"width": 1440, "height": 900})
        page.goto(SITE_URL, wait_until="networkidle")
        web_texts = {
            "about.text": page.text_content(".about .sec-title p") or "",
            "map.ph": page.text_content(".map .ph") or "",
        }
        patch = patch_script(data, web_texts, faces)

        for width, label in WIDTHS:
            goc = OUT_DIR / f"goc-{width}.png"
            web = OUT_DIR / f"web-{width}.png"
            goc.write_bytes(shoot(page, REFERENCE_URL, width, patch))
            web.write_bytes(shoot(page, SITE_URL, width))
            ratio, height_a, height_b = compare_images(goc, web, OUT_DIR / f"lech-{width}.png")
            same_height = "trung" if height_a == height_b else f"LECH {height_b - height_a:+d}px"
            print(f"{width:>5}px ({label:9}): lech {ratio:5.2f}% diem anh  |  cao {height_a}px {same_height}")

        # Do toa do tung phan tu - chac tay hon dem diem anh
        page.set_viewport_size({"width": 1440, "height": 900})
        page.goto(SITE_URL, wait_until="networkidle")
        page.wait_for_timeout(500)
        web_rects = dict(page.evaluate(RECT_JS, SELECTORS))
        page.goto(REFERENCE_URL, wait_until="networkidle")
        page.evaluate(*patch)
        page.wait_for_timeout(500)
        goc_rects = dict(page.evaluate(RECT_JS, SELECTORS))
        browser.close()

    mismatched = [sel for sel in SELECTORS if goc_rects[sel] != web_rects[sel]]
    print(f"\nToa do 1440px: {len(SELECTORS) - len(mismatched)}/{len(SELECTORS)} phan tu trung khop tuyet doi")
    for sel in mismatched:
        print(f"  KHAC {sel}\n       goc {goc_rects[sel]}\n       web {web_rects[sel]}")
    return 1 if mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
