"""Them module kho (warehouse)."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

RESOURCES = (
    ("stock", "tồn kho theo lô", "view,create,update,delete,export"),
    ("receipts", "phiếu nhập kho", "view,create,update,delete,export"),
    ("dispatches", "phiếu xuất kho", "view,create,update,delete,export,approve"),
    ("locations", "vị trí kho", "view,create,update,delete"),
    ("audits", "phiếu kiểm kê", "view,create,update,delete,export"),
)


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS warehouse")

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("warehouse_name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("zone", sa.String(50)),
        sa.Column("shelf", sa.String(50)),
        sa.Column("bin", sa.String(50)),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="warehouse",
    )

    op.create_table(
        "stock_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("common.company_products.id", ondelete="SET NULL")),
        sa.Column("product_code", sa.String(50), nullable=False),
        sa.Column("product_name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="finished"),
        sa.Column("lot_number", sa.String(50), nullable=False),
        sa.Column("expiration_date", sa.Date()),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("warehouse.locations.id", ondelete="SET NULL")),
        sa.Column("location_code", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(30), nullable=False, server_default="kg"),
        sa.Column("hazard_types", sa.String(200)),
        sa.Column("min_threshold", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("max_capacity", sa.Numeric(12, 2), nullable=False, server_default="500"),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="warehouse",
    )

    op.create_table(
        "receipts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("receipt_code", sa.String(50), nullable=False, unique=True),
        sa.Column("receipt_type", sa.String(30), nullable=False, server_default="purchase"),
        sa.Column("supplier_name", sa.String(200)),
        sa.Column("receipt_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="completed"),
        sa.Column("note", sa.Text()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("auth.users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="warehouse",
    )

    op.create_table(
        "receipt_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("receipt_id", sa.Integer(), sa.ForeignKey("warehouse.receipts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_code", sa.String(50), nullable=False),
        sa.Column("product_name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="material"),
        sa.Column("lot_number", sa.String(50), nullable=False),
        sa.Column("expiration_date", sa.Date()),
        sa.Column("location_code", sa.String(50)),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False, server_default="1"),
        sa.Column("unit", sa.String(30), nullable=False, server_default="kg"),
        sa.Column("hazard_types", sa.String(200)),
        schema="warehouse",
    )

    op.create_table(
        "dispatches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dispatch_code", sa.String(50), nullable=False, unique=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("common.customers.id", ondelete="SET NULL")),
        sa.Column("customer_name", sa.String(200), nullable=False),
        sa.Column("dispatch_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("items_summary", sa.String(255)),
        sa.Column("receiver_name", sa.String(100)),
        sa.Column("driver_name", sa.String(100)),
        sa.Column("vehicle_plate", sa.String(50)),
        sa.Column("note", sa.Text()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("auth.users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="warehouse",
    )

    op.create_table(
        "dispatch_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dispatch_id", sa.Integer(), sa.ForeignKey("warehouse.dispatches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_code", sa.String(50), nullable=False),
        sa.Column("product_name", sa.String(200), nullable=False),
        sa.Column("lot_number", sa.String(50)),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False, server_default="1"),
        sa.Column("unit", sa.String(30), nullable=False, server_default="kg"),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        schema="warehouse",
    )

    op.create_table(
        "audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("audit_code", sa.String(50), nullable=False, unique=True),
        sa.Column("warehouse_name", sa.String(100), nullable=False),
        sa.Column("audit_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="completed"),
        sa.Column("auditor_name", sa.String(100)),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="warehouse",
    )

    conn = op.get_bind()
    for resource, label, actions in RESOURCES:
        for action in actions.split(","):
            code = f"warehouse.{resource}.{action}"
            description = f"{action.capitalize()} {label}"
            conn.execute(
                text("INSERT INTO auth.permissions (code, module, description) VALUES (:code, 'warehouse', :description) ON CONFLICT (code) DO NOTHING"),
                {"code": code, "description": description},
            )
            conn.execute(
                text("INSERT INTO auth.role_permissions (role_id, permission_code) SELECT r.id, :code FROM auth.roles r WHERE r.code IN ('admin', 'warehouse') ON CONFLICT DO NOTHING"),
                {"code": code},
            )


def downgrade() -> None:
    for table in ("audits", "dispatch_items", "dispatches", "receipt_items", "receipts", "stock_items", "locations"):
        op.drop_table(table, schema="warehouse")
    op.drop_schema("warehouse")
