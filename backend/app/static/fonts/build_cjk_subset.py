"""Cat ban rut gon cua Noto Serif CJK TC cho letterhead.

Goi font day du nang ~20MB, tai ca goi ve trinh duyet chi de in vai chu Han o
dau phieu thi qua nang. Script nay cat ra dung nhung chu dang dung, con ~10KB.

Chay lai khi doi chu Trung trong letterhead (bang company_profile):

    docker compose run --rm --no-deps backend python app/static/fonts/build_cjk_subset.py

Chu nao khong nam trong ban rut gon thi trinh duyet lui ve font he thong - chi
anh huong khung xem truoc. Ban PDF luon dung font he thong day du trong container.
"""
from __future__ import annotations

import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTCollection

SOURCE = Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc")
TARGET = Path(__file__).resolve().parent / "NotoSerifTC-letterhead.woff2"

# Chu Han cua letterhead + dau cau toan rong, cong them vai chu hay dung phong khi
# sua ten/dia chi. Dung set nen khong lo trung.
LETTERHEAD_TEXT = (
    "越南大亮化工有限公司"
    "越南平陽省新淵縣帝國社帝國工業區 D2 路"
    "電話傳真"
    "：、，。（）「」；！？－～"
    "0123456789"
    "市縣鄉鎮村街道號樓室郵編地址電子信箱網站"
)


def pick_tc_font(collection: TTCollection):
    """File .ttc chua nhieu bo (SC/TC/JP/KR) - lay dung bo TC."""
    for font in collection.fonts:
        for record in font["name"].names:
            if record.nameID == 1 and "TC" in str(record):
                return font
    return collection.fonts[0]


def main() -> None:
    if not SOURCE.exists():
        sys.exit(f"Khong thay {SOURCE} - image backend can goi fonts-noto-cjk")

    font = pick_tc_font(TTCollection(str(SOURCE)))

    options = subset.Options()
    options.flavor = "woff2"
    options.desubroutinize = True
    options.drop_tables += ["DSIG"]
    options.name_IDs = ["*"]
    # .notdef de trong thay vi ve o vuong: chu nao thieu thi trinh duyet
    # lui ve font sau trong stack, khong hien o vuong.
    options.notdef_outline = False

    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text="".join(sorted(set(LETTERHEAD_TEXT))))
    subsetter.subset(font)

    font.flavor = "woff2"
    font.save(str(TARGET))
    print(f"Da tao {TARGET} ({TARGET.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
