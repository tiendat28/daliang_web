"""Them cot / extension cho database da ton tai.

create_all() chi tao bang con thieu, khong them/bo cot -> moi thay doi cot ve sau
phai khai bao o day de khong phai tao lai bang (se mat du lieu dang co).
Moi cau lenh phai chay lai duoc nhieu lan ma khong hong.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.product_catalog import replace_catalog

EXTENSION_STATEMENTS = (
    # unaccent(): tim "nha may z-113" ra duoc "Nha may Z-113" (bo dau tieng Viet)
    "CREATE EXTENSION IF NOT EXISTS unaccent",
)

SCHEMA_STATEMENTS = (
    "ALTER TABLE documents ADD COLUMN IF NOT EXISTS content BYTEA",
    "ALTER TABLE work_logs ADD COLUMN IF NOT EXISTS ot_hours DOUBLE PRECISION",
    "ALTER TABLE company_products ADD COLUMN IF NOT EXISTS name_en VARCHAR(255)",
    "ALTER TABLE company_products ADD COLUMN IF NOT EXISTS category VARCHAR(255)",
    "ALTER TABLE company_products ADD COLUMN IF NOT EXISTS usage_stage VARCHAR(255)",
    "ALTER TABLE company_products ADD COLUMN IF NOT EXISTS materials VARCHAR(255)",
    "ALTER TABLE company_products ADD COLUMN IF NOT EXISTS description TEXT",
)

# SP Cty doi sang danh muc moi (app/data/company_products.json): bo het cot/bang
# thong so kieu cu - du lieu cu duoc thay bang danh muc moi ngay sau do.
LEGACY_PRODUCT_STATEMENTS = (
    "DROP TABLE IF EXISTS company_product_components",
    """
    ALTER TABLE company_products
        DROP COLUMN IF EXISTS field,
        DROP COLUMN IF EXISTS usage_purpose,
        DROP COLUMN IF EXISTS process_stage,
        DROP COLUMN IF EXISTS price,
        DROP COLUMN IF EXISTS unit,
        DROP COLUMN IF EXISTS concentration,
        DROP COLUMN IF EXISTS temperature,
        DROP COLUMN IF EXISTS duration,
        DROP COLUMN IF EXISTS ph
    """,
    "DROP TYPE IF EXISTS processstage",
)


def _has_legacy_products(conn) -> bool:
    return conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = 'company_products' AND column_name = 'field'"
    )).first() is not None


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
        for statement in SCHEMA_STATEMENTS:
            conn.execute(text(statement))

    # Chi chay mot lan: sau lan nay cot "field" da bi bo. Nap danh muc chung
    # transaction voi luc bo cot, loi giua chung thi database van o nguyen kieu cu.
    with engine.begin() as conn:
        if _has_legacy_products(conn):
            for statement in LEGACY_PRODUCT_STATEMENTS:
                conn.execute(text(statement))
            with Session(bind=conn) as db:
                replace_catalog(db)
                db.flush()
