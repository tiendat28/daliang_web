"""Them module nhan su."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

DEPARTMENTS = (("lab", "Kỹ thuật"), ("hr", "Nhân sự"), ("accounting", "Kế toán"), ("warehouse", "Kho"), ("delivery", "Điều phối xe"), ("office", "Văn phòng"))
RESOURCES = (("employees", "hồ sơ nhân viên", "view,create,update,delete,export"), ("attendance", "chấm công", "view,create,update,delete,export"), ("leave_requests", "đơn nghỉ phép", "view,create,update,delete,approve"), ("contracts", "hợp đồng", "view,create,update,delete,export"), ("certificates", "chứng chỉ", "view,create,update,delete,export"), ("departments", "phòng ban", "view,create,update,delete"))


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS hr")
    op.create_table("departments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("code", sa.String(30), nullable=False, unique=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), schema="hr")
    op.create_table("employees", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("auth.users.id", ondelete="SET NULL"), unique=True), sa.Column("employee_code", sa.String(20), nullable=False, unique=True), sa.Column("full_name", sa.String(150), nullable=False), sa.Column("email", sa.String(150)), sa.Column("phone", sa.String(50)), sa.Column("department_code", sa.String(30), sa.ForeignKey("hr.departments.code", ondelete="SET NULL")), sa.Column("position", sa.String(120)), sa.Column("start_date", sa.Date()), sa.Column("contract_end", sa.Date()), sa.Column("status", sa.String(30), nullable=False, server_default="active"), sa.Column("note", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), schema="hr")
    op.create_table("attendance", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("employee_id", sa.Integer(), sa.ForeignKey("hr.employees.id", ondelete="CASCADE"), nullable=False), sa.Column("work_date", sa.Date(), nullable=False), sa.Column("check_in", sa.Time()), sa.Column("check_out", sa.Time()), sa.Column("status", sa.String(30), nullable=False, server_default="present"), sa.Column("note", sa.Text()), sa.UniqueConstraint("employee_id", "work_date", name="uq_hr_attendance_day"), schema="hr")
    op.create_table("leave_requests", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("employee_id", sa.Integer(), sa.ForeignKey("hr.employees.id", ondelete="CASCADE"), nullable=False), sa.Column("leave_type", sa.String(50), nullable=False, server_default="annual"), sa.Column("start_date", sa.Date(), nullable=False), sa.Column("end_date", sa.Date(), nullable=False), sa.Column("reason", sa.Text()), sa.Column("status", sa.String(30), nullable=False, server_default="pending"), sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("auth.users.id", ondelete="SET NULL")), sa.Column("reviewed_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), schema="hr")
    op.create_table("contracts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("employee_id", sa.Integer(), sa.ForeignKey("hr.employees.id", ondelete="CASCADE"), nullable=False), sa.Column("contract_type", sa.String(80), nullable=False), sa.Column("start_date", sa.Date(), nullable=False), sa.Column("end_date", sa.Date()), sa.Column("status", sa.String(30), nullable=False, server_default="active"), sa.Column("note", sa.Text()), schema="hr")
    op.create_table("certificates", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("employee_id", sa.Integer(), sa.ForeignKey("hr.employees.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(180), nullable=False), sa.Column("issuer", sa.String(150)), sa.Column("issued_date", sa.Date()), sa.Column("expires_at", sa.Date()), sa.Column("note", sa.Text()), schema="hr")
    conn = op.get_bind()
    for code, name in DEPARTMENTS:
        conn.execute(text("INSERT INTO hr.departments (code, name) VALUES (:code, :name) ON CONFLICT (code) DO NOTHING"), {"code": code, "name": name})
    conn.execute(text("INSERT INTO hr.employees (user_id, employee_code, full_name, email, department_code, status) SELECT id, COALESCE(employee_code, 'USER-' || id), full_name, email, department, CASE WHEN is_active THEN 'active' ELSE 'inactive' END FROM auth.users WHERE deleted_at IS NULL ON CONFLICT (user_id) DO NOTHING"))
    for resource, label, actions in RESOURCES:
        for action in actions.split(","):
            code = f"hr.{resource}.{action}"
            description = f"{'Duyệt' if action == 'approve' else action.capitalize()} {label}"
            conn.execute(text("INSERT INTO auth.permissions (code, module, description) VALUES (:code, 'hr', :description) ON CONFLICT (code) DO NOTHING"), {"code": code, "description": description})
            conn.execute(text("INSERT INTO auth.role_permissions (role_id, permission_code) SELECT r.id, :code FROM auth.roles r WHERE r.code IN ('admin', 'hr') ON CONFLICT DO NOTHING"), {"code": code})


def downgrade() -> None:
    for table in ("certificates", "contracts", "leave_requests", "attendance", "employees", "departments"):
        op.drop_table(table, schema="hr")
    op.drop_schema("hr")
