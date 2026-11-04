"""Quyen 6 hanh dong, ma nhan vien + bo phan, xoa mem tai khoan, ghi nho thiet bi, cau tom tat nhat ky.

- auth.users: them employee_code, department, deleted_at. Email / ma NV chi can
  khong trung giua tai khoan CHUA xoa (unique index co dieu kien).
- auth.refresh_tokens.remember: phien "ghi nho thiet bi 30 ngay".
- system.audit_logs.summary: cau de doc ("Sửa đơn hàng HCTN #5").
- Quyen `<x>.edit` tach thanh `<x>.create` / `.update` / `.delete`; vai tro dang
  co `.edit` duoc giu nguyen kha nang (nhan ca ba). Ai co `.view` cua cac chuc
  nang xuat duoc file thi nhan them `.export` (truoc day xuat file khong can quyen).
  Mo ta quyen se duoc sync_permissions() ghi lai dung luc backend khoi dong.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-23
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

# Chuc nang co quyen xuat file (khop voi <module>/permissions.py luc nay)
EXPORTABLE = (
    "common.customers", "common.products",
    "lab.chemicals", "lab.indicators", "lab.equipment", "lab.formulations", "lab.samples",
    "lab.analysis_reports", "lab.work_logs", "lab.test_processes",
)
# .edit cua cac chuc nang nay chi con .update (khong co them/xoa)
UPDATE_ONLY = ("common.company_profile", "website.contact_leads")


def _grant(conn, new_code: str, from_code: str) -> None:
    """Tao quyen new_code (neu chua co) va cap cho moi vai tro dang giu from_code."""
    conn.execute(text(
        "INSERT INTO auth.permissions (code, module, description) "
        "VALUES (:code, split_part(:code, '.', 1), :code) ON CONFLICT (code) DO NOTHING"
    ), {"code": new_code})
    conn.execute(text(
        "INSERT INTO auth.role_permissions (role_id, permission_code) "
        "SELECT role_id, :new FROM auth.role_permissions WHERE permission_code = :old "
        "ON CONFLICT DO NOTHING"
    ), {"new": new_code, "old": from_code})


def upgrade() -> None:
    op.add_column("users", sa.Column("employee_code", sa.String(length=20), nullable=True), schema="auth")
    op.add_column("users", sa.Column("department", sa.String(length=30), nullable=True), schema="auth")
    op.add_column("users", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), schema="auth")
    op.drop_index("ix_users_email", table_name="users", schema="auth")
    op.create_index("ix_users_email", "users", ["email"], unique=True, schema="auth",
                    postgresql_where=text("deleted_at IS NULL"))
    op.create_index("ix_users_employee_code", "users", ["employee_code"], unique=True, schema="auth",
                    postgresql_where=text("deleted_at IS NULL"))
    op.add_column("refresh_tokens", sa.Column("remember", sa.Boolean(), nullable=False, server_default=sa.false()),
                  schema="auth")
    op.alter_column("refresh_tokens", "remember", server_default=None, schema="auth")
    op.add_column("audit_logs", sa.Column("summary", sa.String(length=255), nullable=True), schema="system")

    conn = op.get_bind()
    edit_codes = [row[0] for row in conn.execute(text(
        "SELECT code FROM auth.permissions WHERE code LIKE '%.edit'"))]
    for code in edit_codes:
        base = code[: -len(".edit")]
        actions = ("update",) if base in UPDATE_ONLY else ("create", "update", "delete")
        for action in actions:
            _grant(conn, f"{base}.{action}", code)
    for base in EXPORTABLE:
        _grant(conn, f"{base}.export", f"{base}.view")
    # role_permissions tro toi permissions voi ON DELETE CASCADE
    conn.execute(text("DELETE FROM auth.permissions WHERE code LIKE '%.edit'"))


def downgrade() -> None:
    op.drop_column("audit_logs", "summary", schema="system")
    op.drop_column("refresh_tokens", "remember", schema="auth")
    op.drop_index("ix_users_employee_code", table_name="users", schema="auth")
    op.drop_index("ix_users_email", table_name="users", schema="auth")
    op.create_index("ix_users_email", "users", ["email"], unique=True, schema="auth")
    op.drop_column("users", "deleted_at", schema="auth")
    op.drop_column("users", "department", schema="auth")
    op.drop_column("users", "employee_code", schema="auth")
