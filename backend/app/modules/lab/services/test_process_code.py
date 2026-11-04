"""Sinh ma luu trinh LT-YYYY-NNN."""
from __future__ import annotations

import re
from datetime import date

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.modules.lab.models import TestProcess

CODE_PREFIX = "LT"
_CODE_RE = re.compile(r"^LT-(\d{4})-(\d{3,})$")


def next_process_code(db: Session, year: int | None = None) -> str:
    """Ma tiep theo cua nam, vd "LT-2026-012".

    Phai goi trong transaction dang mo. Advisory lock giu cho 2 request tao cung
    luc khong lay trung mot so; lock tu nha khi transaction ket thuc.
    """
    year = year or date.today().year
    bind = db.get_bind()
    if bind is not None and bind.dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
                   {"key": f"test_process_code:{year}"})

    prefix = f"{CODE_PREFIX}-{year}-"
    # Tinh ca luu trinh da xoa mem: ma da cap thi khong cap lai
    codes = db.execute(
        select(TestProcess.code).where(TestProcess.code.like(f"{prefix}%"))
    ).scalars().all()

    highest = 0
    for code in codes:
        match = _CODE_RE.match(code or "")
        if match and int(match.group(1)) == year:
            highest = max(highest, int(match.group(2)))
    return f"{prefix}{highest + 1:03d}"
