"""Them module dieu phoi xe (dispatch)."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

RESOURCES = (
    ("trips", "chuyến giao hàng", "view,create,update,delete,export,approve"),
    ("vehicles", "xe giao hàng", "view,create,update,delete"),
    ("drivers", "tài xế", "view,create,update,delete"),
)


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS dispatch")

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plate_number", sa.String(50), nullable=False, unique=True),
        sa.Column("vehicle_type", sa.String(50), nullable=False, server_default="Xe tải 1.5 tấn"),
        sa.Column("max_payload_kg", sa.Numeric(10, 2), server_default="1500"),
        sa.Column("hazard_permit_expiry", sa.Date()),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="dispatch",
    )

    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("auth.users.id", ondelete="SET NULL")),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20)),
        sa.Column("license_number", sa.String(50)),
        sa.Column("license_class", sa.String(20), server_default="C"),
        sa.Column("hazard_training_expiry", sa.Date()),
        sa.Column("default_vehicle_id", sa.Integer(), sa.ForeignKey("dispatch.vehicles.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(30), nullable=False, server_default="ready"),  # running, ready, issue, off
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="dispatch",
    )

    op.create_table(
        "delivery_trips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trip_code", sa.String(50), nullable=False, unique=True),
        sa.Column("dispatch_code", sa.String(50), nullable=False),
        sa.Column("dispatch_order_id", sa.Integer(), sa.ForeignKey("warehouse.dispatches.id", ondelete="SET NULL")),
        sa.Column("customer_name", sa.String(200), nullable=False),
        sa.Column("customer_address", sa.String(255)),
        sa.Column("items_summary", sa.String(255)),
        sa.Column("is_hazardous", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("driver_id", sa.Integer(), sa.ForeignKey("dispatch.drivers.id", ondelete="SET NULL")),
        sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("dispatch.vehicles.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(30), nullable=False, server_default="unassigned"),  # unassigned, delivering, delivered, issue
        sa.Column("estimated_time", sa.String(50)),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
        sa.Column("proof_image_url", sa.String(255)),
        sa.Column("issue_note", sa.Text()),
        sa.Column("trip_date", sa.Date(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("auth.users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="dispatch",
    )

    conn = op.get_bind()
    for resource, label, actions in RESOURCES:
        for action in actions.split(","):
            code = f"dispatch.{resource}.{action}"
            description = f"{action.capitalize()} {label}"
            conn.execute(
                text("INSERT INTO auth.permissions (code, module, description) VALUES (:code, 'dispatch', :description) ON CONFLICT (code) DO NOTHING"),
                {"code": code, "description": description},
            )
            conn.execute(
                text("INSERT INTO auth.role_permissions (role_id, permission_code) SELECT r.id, :code FROM auth.roles r WHERE r.code IN ('admin', 'dispatch') ON CONFLICT DO NOTHING"),
                {"code": code},
            )


def downgrade() -> None:
    for table in ("delivery_trips", "drivers", "vehicles"):
        op.drop_table(table, schema="dispatch")
    op.drop_schema("dispatch")
