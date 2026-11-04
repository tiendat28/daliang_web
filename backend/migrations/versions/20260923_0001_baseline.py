"""Ban goc: chia bang vao schema theo module.

Chay duoc tren ca hai loai database:
  - DB trong (may moi): tao schema roi tao du bang tu model.
  - DB dang dung truoc khi co Alembic (moi bang nam o `public`, cot duoc them
    dan bang app/core/migrations.py cu): chuyen tung bang sang schema cua no
    bang ALTER TABLE ... SET SCHEMA - GIU NGUYEN du lieu, id, khoa ngoai -
    roi bu nhung cot con thieu.

Cau truc bang viet cung trong _create_missing_tables() (dong bang ngay 23/09/2026),
khong doc tu model - model doi ve sau khong lam ban nay doi theo.

Revision ID: 0001
Revises:
Create Date: 2026-09-23
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Text, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMAS = ("common", "lab", "website")

# bang -> schema moi (cac bang truoc day nam het o public)
TABLE_SCHEMAS = {
    "common": (
        "customers", "customer_fields", "customer_field_products",
        "company_products", "company_product_modes", "company_profile", "documents",
    ),
    "lab": (
        "lab_chemicals", "indicators", "equipment", "equipment_variants",
        "chemical_orders", "chemical_sampling",
        "analysis_reports", "analysis_completed_by", "analysis_samples", "analysis_components",
        "work_logs", "test_processes", "test_process_steps",
        "test_process_step_concentrations", "test_process_step_chemicals", "process_templates",
    ),
    "website": ("contact_leads",),
}

# Cot them dan truoc khi co Alembic (tu app/core/migrations.py cu). DB nao da
# co thi IF NOT EXISTS bo qua; DB trong thi bang chua co nen IF EXISTS bo qua.
MISSING_COLUMNS = (
    "ALTER TABLE IF EXISTS common.documents ADD COLUMN IF NOT EXISTS content BYTEA",
    "ALTER TABLE IF EXISTS lab.work_logs ADD COLUMN IF NOT EXISTS ot_hours DOUBLE PRECISION",
    "ALTER TABLE IF EXISTS common.company_products ADD COLUMN IF NOT EXISTS name_en VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_products ADD COLUMN IF NOT EXISTS category VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_products ADD COLUMN IF NOT EXISTS usage_stage VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_products ADD COLUMN IF NOT EXISTS materials VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_products ADD COLUMN IF NOT EXISTS description TEXT",
    "ALTER TABLE IF EXISTS common.company_products ADD COLUMN IF NOT EXISTS name_zh VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_products ADD COLUMN IF NOT EXISTS description_en TEXT",
    "ALTER TABLE IF EXISTS common.company_products ADD COLUMN IF NOT EXISTS description_zh TEXT",
    "ALTER TABLE IF EXISTS common.company_products ADD COLUMN IF NOT EXISTS web_group VARCHAR(10)",
    "ALTER TABLE IF EXISTS common.company_profile ADD COLUMN IF NOT EXISTS name_vi VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_profile ADD COLUMN IF NOT EXISTS address_vi VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_profile ADD COLUMN IF NOT EXISTS tax_id VARCHAR(100)",
    "ALTER TABLE IF EXISTS common.company_profile ADD COLUMN IF NOT EXISTS email VARCHAR(150)",
    "ALTER TABLE IF EXISTS common.company_profile ADD COLUMN IF NOT EXISTS hours_vi VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_profile ADD COLUMN IF NOT EXISTS hours_en VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_profile ADD COLUMN IF NOT EXISTS hours_zh VARCHAR(255)",
    "ALTER TABLE IF EXISTS common.company_profile ADD COLUMN IF NOT EXISTS map_query VARCHAR(500)",
)

# SP Cty kieu cu (co cot "field"): bo cot/bang thong so cu, du lieu thay bang
# danh muc moi ngay sau do.
LEGACY_PRODUCT_STATEMENTS = (
    "DROP TABLE IF EXISTS public.company_product_components",
    """
    ALTER TABLE common.company_products
        DROP COLUMN IF EXISTS field, DROP COLUMN IF EXISTS usage_purpose,
        DROP COLUMN IF EXISTS process_stage, DROP COLUMN IF EXISTS price,
        DROP COLUMN IF EXISTS unit, DROP COLUMN IF EXISTS concentration,
        DROP COLUMN IF EXISTS temperature, DROP COLUMN IF EXISTS duration,
        DROP COLUMN IF EXISTS ph
    """,
    "DROP TYPE IF EXISTS processstage",
)


def _exists(conn, schema: str, table: str) -> bool:
    return conn.execute(text("SELECT to_regclass(:name) IS NOT NULL"), {"name": f"{schema}.{table}"}).scalar()


def upgrade() -> None:
    conn = op.get_bind()

    # unaccent(): tim "nha may z-113" ra "Nha may Z-113". Savepoint rieng: thieu
    # quyen tao extension thi chi mat tim khong dau, khong hong ca migration.
    try:
        with conn.begin_nested():
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
    except Exception:  # noqa: BLE001 - loi quyen tren DB dung chung, bo qua co chu dich
        pass

    for schema in SCHEMAS:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

    for schema, tables in TABLE_SCHEMAS.items():
        for table in tables:
            if _exists(conn, "public", table) and not _exists(conn, schema, table):
                conn.execute(text(f"ALTER TABLE public.{table} SET SCHEMA {schema}"))

    # Ban website dau tien (23/09/2026) co 3 bang rieng, noi dung da chuyen sang
    # common.company_products / company_profile / documents
    for table in ("web_products", "web_documents", "web_company_info"):
        conn.execute(text(f"DROP TABLE IF EXISTS public.{table}"))

    for statement in MISSING_COLUMNS:
        conn.execute(text(statement))
    if _exists(conn, "common", "company_products"):
        # cung ten voi index=True cua model (quy uoc ix_<bang>_<cot>)
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_company_products_web_group ON common.company_products (web_group)"
        ))
    conn.execute(text("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'documentcategory') THEN
                ALTER TYPE documentcategory ADD VALUE IF NOT EXISTS 'certificate';
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_schema = 'website' AND table_name = 'contact_leads'
                         AND column_name = 'is_handled' AND data_type = 'integer') THEN
                ALTER TABLE website.contact_leads ALTER COLUMN is_handled DROP DEFAULT;
                ALTER TABLE website.contact_leads ALTER COLUMN is_handled TYPE BOOLEAN USING is_handled <> 0;
            END IF;
        END $$
    """))

    # Bang con thieu (DB trong: tat ca)
    _create_missing_tables(conn)

    has_legacy_products = conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_schema = 'common' AND table_name = 'company_products' AND column_name = 'field'"
    )).first()
    if has_legacy_products:
        from app.modules.common.services.catalog import replace_catalog
        for statement in LEGACY_PRODUCT_STATEMENTS:
            conn.execute(text(statement))
        with Session(bind=conn) as db:
            replace_catalog(db)
            db.flush()


def _create_missing_tables(conn) -> None:
    """Cau truc 24 bang tai thoi diem 23/09/2026 (sinh bang alembic tu model luc do,
    DONG BANG - khong sua theo model ve sau). Bang nao da co thi bo qua."""
    if not _exists(conn, 'common', 'company_products'):
        op.create_table('company_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('name_en', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=255), nullable=True),
        sa.Column('usage_stage', sa.String(length=255), nullable=True),
        sa.Column('materials', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('name_zh', sa.String(length=255), nullable=True),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_zh', sa.Text(), nullable=True),
        sa.Column('web_group', sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='common'
        )
        op.create_index(op.f('ix_company_products_code'), 'company_products', ['code'], unique=True, schema='common')
        op.create_index(op.f('ix_company_products_id'), 'company_products', ['id'], unique=False, schema='common')
        op.create_index(op.f('ix_company_products_web_group'), 'company_products', ['web_group'], unique=False, schema='common')
    if not _exists(conn, 'common', 'company_profile'):
        op.create_table('company_profile',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('logo_path', sa.String(length=255), nullable=True),
        sa.Column('name_zh', sa.String(length=255), nullable=True),
        sa.Column('name_en', sa.String(length=255), nullable=True),
        sa.Column('address_zh', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=100), nullable=True),
        sa.Column('fax', sa.String(length=100), nullable=True),
        sa.Column('name_vi', sa.String(length=255), nullable=True),
        sa.Column('address_vi', sa.String(length=255), nullable=True),
        sa.Column('tax_id', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=150), nullable=True),
        sa.Column('hours_vi', sa.String(length=255), nullable=True),
        sa.Column('hours_en', sa.String(length=255), nullable=True),
        sa.Column('hours_zh', sa.String(length=255), nullable=True),
        sa.Column('map_query', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='common'
        )
        op.create_index(op.f('ix_company_profile_id'), 'company_profile', ['id'], unique=False, schema='common')
    if not _exists(conn, 'common', 'customers'):
        op.create_table('customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='common'
        )
        op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False, schema='common')
    if not _exists(conn, 'common', 'documents'):
        op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.Enum('msds', 'coa', 'technical', 'method_analysis', 'certificate', name='documentcategory'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('stored_filename', sa.String(length=255), nullable=False),
        sa.Column('content', sa.LargeBinary(), nullable=True),
        sa.Column('mime_type', sa.String(length=150), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('uploaded_by', sa.String(length=150), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='common'
        )
        op.create_index(op.f('ix_documents_category'), 'documents', ['category'], unique=False, schema='common')
        op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False, schema='common')
    if not _exists(conn, 'lab', 'equipment'):
        op.create_table('equipment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_equipment_id'), 'equipment', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'indicators'):
        op.create_table('indicators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_indicators_id'), 'indicators', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'lab_chemicals'):
        op.create_table('lab_chemicals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=True),
        sa.Column('box_count', sa.Float(), nullable=True),
        sa.Column('volume_per_box', sa.Float(), nullable=True),
        sa.Column('total_volume', sa.Float(), nullable=True),
        sa.Column('remaining_volume', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_lab_chemicals_code'), 'lab_chemicals', ['code'], unique=True, schema='lab')
        op.create_index(op.f('ix_lab_chemicals_id'), 'lab_chemicals', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'process_templates'):
        op.create_table('process_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('steps', postgresql.JSONB(astext_type=Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        schema='lab'
        )
        op.create_index(op.f('ix_process_templates_id'), 'process_templates', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'work_logs'):
        op.create_table('work_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('log_date', sa.Date(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('ot_hours', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_work_logs_id'), 'work_logs', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'website', 'contact_leads'):
        op.create_table('contact_leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=True),
        sa.Column('product', sa.String(length=255), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('lang', sa.String(length=5), nullable=True),
        sa.Column('source_path', sa.String(length=255), nullable=True),
        sa.Column('is_handled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='website'
        )
        op.create_index(op.f('ix_contact_leads_id'), 'contact_leads', ['id'], unique=False, schema='website')
    if not _exists(conn, 'common', 'company_product_modes'):
        op.create_table('company_product_modes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('params', postgresql.JSONB(astext_type=Text()), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['common.company_products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='common'
        )
        op.create_index(op.f('ix_company_product_modes_id'), 'company_product_modes', ['id'], unique=False, schema='common')
        op.create_index(op.f('ix_company_product_modes_product_id'), 'company_product_modes', ['product_id'], unique=False, schema='common')
    if not _exists(conn, 'common', 'customer_fields'):
        op.create_table('customer_fields',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['common.customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='common'
        )
        op.create_index(op.f('ix_customer_fields_id'), 'customer_fields', ['id'], unique=False, schema='common')
    if not _exists(conn, 'lab', 'analysis_reports'):
        op.create_table('analysis_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('sample_receive_date', sa.Date(), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['common.customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_analysis_reports_id'), 'analysis_reports', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'chemical_orders'):
        op.create_table('chemical_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lab_chemical_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=True),
        sa.Column('concentration', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.String(length=100), nullable=True),
        sa.Column('order_quantity', sa.String(length=100), nullable=True),
        sa.Column('used_amount', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('mix_date', sa.Date(), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['common.customers.id'], ),
        sa.ForeignKeyConstraint(['lab_chemical_id'], ['lab.lab_chemicals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_chemical_orders_id'), 'chemical_orders', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'chemical_sampling'):
        op.create_table('chemical_sampling',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_product_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('sample_date', sa.Date(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['company_product_id'], ['common.company_products.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_chemical_sampling_id'), 'chemical_sampling', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'equipment_variants'):
        op.create_table('equipment_variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.Integer(), nullable=False),
        sa.Column('classification', sa.String(length=100), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['lab.equipment.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_equipment_variants_id'), 'equipment_variants', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'test_processes'):
        op.create_table('test_processes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('customer_name', sa.String(length=255), nullable=False),
        sa.Column('requirement', sa.Text(), nullable=True),
        sa.Column('sample_quantity', sa.Integer(), nullable=False),
        sa.Column('test_month', sa.Date(), nullable=False),
        sa.Column('prepared_by', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('internal_note', sa.Text(), nullable=True),
        sa.Column('source_process_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('sample_quantity > 0', name='ck_test_processes_sample_quantity_positive'),
        sa.ForeignKeyConstraint(['customer_id'], ['common.customers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['source_process_id'], ['lab.test_processes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_test_processes_code'), 'test_processes', ['code'], unique=True, schema='lab')
        op.create_index(op.f('ix_test_processes_customer_id'), 'test_processes', ['customer_id'], unique=False, schema='lab')
        op.create_index(op.f('ix_test_processes_deleted_at'), 'test_processes', ['deleted_at'], unique=False, schema='lab')
        op.create_index(op.f('ix_test_processes_id'), 'test_processes', ['id'], unique=False, schema='lab')
        op.create_index(op.f('ix_test_processes_status'), 'test_processes', ['status'], unique=False, schema='lab')
    if not _exists(conn, 'common', 'customer_field_products'):
        op.create_table('customer_field_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_field_id', sa.Integer(), nullable=False),
        sa.Column('company_product_id', sa.Integer(), nullable=True),
        sa.Column('product_code_text', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['company_product_id'], ['common.company_products.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['customer_field_id'], ['common.customer_fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='common'
        )
        op.create_index(op.f('ix_customer_field_products_id'), 'customer_field_products', ['id'], unique=False, schema='common')
    if not _exists(conn, 'lab', 'analysis_completed_by'):
        op.create_table('analysis_completed_by',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['lab.analysis_reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_analysis_completed_by_id'), 'analysis_completed_by', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'analysis_samples'):
        op.create_table('analysis_samples',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['lab.analysis_reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_analysis_samples_id'), 'analysis_samples', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'test_process_steps'):
        op.create_table('test_process_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('process_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('operation', sa.String(length=255), nullable=False),
        sa.Column('time_min', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('time_max', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('time_unit', sa.String(length=10), nullable=True),
        sa.Column('temp_mode', sa.String(length=10), nullable=False),
        sa.Column('temp_min', sa.Numeric(precision=6, scale=1), nullable=True),
        sa.Column('temp_max', sa.Numeric(precision=6, scale=1), nullable=True),
        sa.Column('ph_min', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('ph_max', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('time_text', sa.String(length=100), nullable=True),
        sa.Column('temp_text', sa.String(length=100), nullable=True),
        sa.Column('ph_text', sa.String(length=100), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.CheckConstraint('ph_max IS NULL OR (ph_max >= 0 AND ph_max <= 14)', name='ck_test_process_steps_ph_max_range'),
        sa.CheckConstraint('ph_min IS NULL OR (ph_min >= 0 AND ph_min <= 14)', name='ck_test_process_steps_ph_min_range'),
        sa.ForeignKeyConstraint(['process_id'], ['lab.test_processes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('process_id', 'position', name='uq_test_process_steps_position'),
        schema='lab'
        )
        op.create_index(op.f('ix_test_process_steps_id'), 'test_process_steps', ['id'], unique=False, schema='lab')
        op.create_index(op.f('ix_test_process_steps_process_id'), 'test_process_steps', ['process_id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'analysis_components'):
        op.create_table('analysis_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sample_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('result', sa.String(length=100), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['sample_id'], ['lab.analysis_samples.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_analysis_components_id'), 'analysis_components', ['id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'test_process_step_chemicals'):
        op.create_table('test_process_step_chemicals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('step_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('lab_chemical_id', sa.Integer(), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.CheckConstraint('product_id IS NULL OR lab_chemical_id IS NULL', name='ck_test_process_step_chemicals_single_source'),
        sa.ForeignKeyConstraint(['lab_chemical_id'], ['lab.lab_chemicals.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['product_id'], ['common.company_products.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['step_id'], ['lab.test_process_steps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_test_process_step_chemicals_id'), 'test_process_step_chemicals', ['id'], unique=False, schema='lab')
        op.create_index(op.f('ix_test_process_step_chemicals_lab_chemical_id'), 'test_process_step_chemicals', ['lab_chemical_id'], unique=False, schema='lab')
        op.create_index(op.f('ix_test_process_step_chemicals_product_id'), 'test_process_step_chemicals', ['product_id'], unique=False, schema='lab')
        op.create_index(op.f('ix_test_process_step_chemicals_step_id'), 'test_process_step_chemicals', ['step_id'], unique=False, schema='lab')
    if not _exists(conn, 'lab', 'test_process_step_concentrations'):
        op.create_table('test_process_step_concentrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('step_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('component', sa.String(length=50), nullable=True),
        sa.Column('value_min', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('value_max', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('text_override', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['step_id'], ['lab.test_process_steps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='lab'
        )
        op.create_index(op.f('ix_test_process_step_concentrations_id'), 'test_process_step_concentrations', ['id'], unique=False, schema='lab')
        op.create_index(op.f('ix_test_process_step_concentrations_step_id'), 'test_process_step_concentrations', ['step_id'], unique=False, schema='lab')


def downgrade() -> None:
    raise NotImplementedError("Ban goc khong ha xuong duoc - khoi phuc tu ban sao luu neu can.")
