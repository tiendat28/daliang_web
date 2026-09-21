"""Them cot / extension cho database da ton tai.

create_all() chi tao bang con thieu, khong them cot -> moi cot bo sung ve sau
phai khai bao o day de khong phai tao lai bang (se mat du lieu dang co).
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine

EXTENSION_STATEMENTS = (
    # unaccent(): tim "nha may z-113" ra duoc "Nha may Z-113" (bo dau tieng Viet)
    "CREATE EXTENSION IF NOT EXISTS unaccent",
)

ADD_COLUMN_STATEMENTS = (
    "ALTER TABLE documents ADD COLUMN IF NOT EXISTS content BYTEA",
    "ALTER TABLE work_logs ADD COLUMN IF NOT EXISTS ot_hours DOUBLE PRECISION",
)


def run_startup_migrations(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":  # cu phap IF NOT EXISTS rieng cua Postgres
        return
    for statement in EXTENSION_STATEMENTS:
        # Tach transaction rieng: thieu quyen tao extension thi chi mat tim khong dau,
        # khong duoc keo do ca cac migration con lai.
        try:
            with engine.begin() as conn:
                conn.execute(text(statement))
        except Exception:  # noqa: BLE001 - loi quyen tren DB dung chung, bo qua co chu dich
            pass
    with engine.begin() as conn:
        for statement in ADD_COLUMN_STATEMENTS:
            conn.execute(text(statement))
