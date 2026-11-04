"""Them module ke toan."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

RESOURCES = (
    ("invoices", "hoá đơn", "view,create,update,delete,export"),
    ("vouchers", "phiếu thu chi", "view,create,update,delete,export"),
    ("receivables", "công nợ phải thu", "view,export"),
    ("payables", "công nợ phải trả", "view,export"),
    ("cashbook", "sổ quỹ", "view,export"),
    ("reports", "báo cáo tài chính kế toán", "view,export"),
)


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS accounting")

    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_type", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("account_number", sa.String(50)),
        sa.Column("bank_name", sa.String(100)),
        sa.Column("current_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="accounting",
    )

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("invoice_code", sa.String(30), nullable=False, unique=True),
        sa.Column("invoice_type", sa.String(20), nullable=False, server_default="sales"),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("common.customers.id", ondelete="SET NULL")),
        sa.Column("customer_name", sa.String(200), nullable=False),
        sa.Column("supplier_name", sa.String(200)),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date()),
        sa.Column("subtotal", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default="10"),
        sa.Column("tax_amount", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("paid_amount", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("payment_status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("einvoice_status", sa.String(30), nullable=False, server_default="issued"),
        sa.Column("einvoice_number", sa.String(50)),
        sa.Column("note", sa.Text()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("auth.users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="accounting",
    )

    op.create_table(
        "invoice_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("invoice_id", sa.Integer(), sa.ForeignKey("accounting.invoices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("common.company_products.id", ondelete="SET NULL")),
        sa.Column("product_code", sa.String(50)),
        sa.Column("product_name", sa.String(200), nullable=False),
        sa.Column("unit", sa.String(30), nullable=False, server_default="Kg"),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default="10"),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False, server_default="0"),
        schema="accounting",
    )

    op.create_table(
        "vouchers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("voucher_code", sa.String(30), nullable=False, unique=True),
        sa.Column("voucher_type", sa.String(10), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="sales_receipt"),
        sa.Column("payment_method", sa.String(20), nullable=False, server_default="bank"),
        sa.Column("bank_account", sa.String(50)),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("partner_name", sa.String(200), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("common.customers.id", ondelete="SET NULL")),
        sa.Column("invoice_id", sa.Integer(), sa.ForeignKey("accounting.invoices.id", ondelete="SET NULL")),
        sa.Column("voucher_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("auth.users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="accounting",
    )

    conn = op.get_bind()
    for resource, label, actions in RESOURCES:
        for action in actions.split(","):
            code = f"accounting.{resource}.{action}"
            description = f"{action.capitalize()} {label}"
            conn.execute(
                text("INSERT INTO auth.permissions (code, module, description) VALUES (:code, 'accounting', :description) ON CONFLICT (code) DO NOTHING"),
                {"code": code, "description": description},
            )
            conn.execute(
                text("INSERT INTO auth.role_permissions (role_id, permission_code) SELECT r.id, :code FROM auth.roles r WHERE r.code IN ('admin', 'accounting') ON CONFLICT DO NOTHING"),
                {"code": code},
            )


def downgrade() -> None:
    for table in ("vouchers", "invoice_items", "invoices", "bank_accounts"):
        op.drop_table(table, schema="accounting")
    op.drop_schema("accounting")
