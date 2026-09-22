"""Them cot / extension cho database da ton tai.

create_all() chi tao bang con thieu, khong them/bo cot -> moi thay doi cot ve sau
phai khai bao o day de khong phai tao lai bang (se mat du lieu dang co).
Moi cau lenh phai chay lai duoc nhieu lan ma khong hong.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine

EXTENSION_STATEMENTS = (
    # unaccent(): tim "nha may z-113" ra duoc "Nha may Z-113" (bo dau tieng Viet)
    "CREATE EXTENSION IF NOT EXISTS unaccent",
)

SCHEMA_STATEMENTS = (
    "ALTER TABLE documents ADD COLUMN IF NOT EXISTS content BYTEA",
    "ALTER TABLE work_logs ADD COLUMN IF NOT EXISTS ot_hours DOUBLE PRECISION",
    "ALTER TABLE company_products ADD COLUMN IF NOT EXISTS temperature VARCHAR(100)",
    "ALTER TABLE company_products ADD COLUMN IF NOT EXISTS duration VARCHAR(100)",
    "ALTER TABLE company_products ADD COLUMN IF NOT EXISTS ph VARCHAR(50)",
    # SP Cty bo cot don vi: don vi gio viet thang trong nong do ("5" + "ml/L"
    # -> "5 ml/L"). Gop chu cu vao roi moi bo cot, de khong mat du lieu dang co.
    """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'company_products' AND column_name = 'unit'
        ) THEN
            UPDATE company_products
               SET concentration = trim(concat_ws(' ', nullif(concentration, ''), unit))
             WHERE nullif(unit, '') IS NOT NULL;
            ALTER TABLE company_products DROP COLUMN unit;
        END IF;
    END $$;
    """,
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
        for statement in SCHEMA_STATEMENTS:
            conn.execute(text(statement))
