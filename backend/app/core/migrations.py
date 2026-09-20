"""Them cot moi cho bang da ton tai.

create_all() chi tao bang con thieu, khong them cot -> moi cot bo sung ve sau
phai khai bao o day de khong phai tao lai bang (se mat du lieu dang co).
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine

ADD_COLUMN_STATEMENTS = (
    "ALTER TABLE documents ADD COLUMN IF NOT EXISTS content BYTEA",
    "ALTER TABLE work_logs ADD COLUMN IF NOT EXISTS ot_hours DOUBLE PRECISION",
)


def run_startup_migrations(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":  # cu phap IF NOT EXISTS rieng cua Postgres
        return
    with engine.begin() as conn:
        for statement in ADD_COLUMN_STATEMENTS:
            conn.execute(text(statement))
