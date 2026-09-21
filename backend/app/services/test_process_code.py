"""Sinh ma luu trinh LT-YYYY-NNN."""
from __future__ import annotations

import re
from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

CODE_PREFIX = "LT"
_CODE_RE = re.compile(r"^LT-(\d{4})-(\d{3,})$")


def next_process_code(db: Session, year: int | None = None) -> str:
    """Ma tiep theo cua nam, vd "LT-2026-012".

    Phai goi trong transaction dang mo. Advisory lock giu cho 2 request tao cung
    luc khong lay trung mot so; lock tu nha khi transaction ket thuc.
    """
    year = year or date.today().year
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
                   {"key": f"test_process_code:{year}"})

    prefix = f"{CODE_PREFIX}-{year}-"
    codes = db.execute(
        text("SELECT code FROM test_processes WHERE code LIKE :pattern"),
        {"pattern": f"{prefix}%"},
    ).scalars().all()

    highest = 0
    for code in codes:
        match = _CODE_RE.match(code or "")
        if match and int(match.group(1)) == year:
            highest = max(highest, int(match.group(2)))
    return f"{prefix}{highest + 1:03d}"
