"""Tao tai khoan Admin cao nhat - chay tay trong container backend:

    docker compose -f infra/docker-compose.yml exec backend python -m app.modules.auth.create_admin
    (Railway: mo Shell cua service backend roi chay `python -m app.modules.auth.create_admin`)

Hoi email, ho ten, mat khau (go an). Khong co terminal de go (chay tu script)
thi them --email, --name va --generate-password: in ra mat khau tam, bat buoc
doi o lan dang nhap dau. Lan dang nhap dau cung bat buoc cai 2FA (vai tro admin).

Email da co thi chi gan them vai tro admin, khong doi mat khau.
"""
import argparse
import getpass
import secrets
import sys

from app.core.database import SessionLocal
from app.core.security import hash_password, password_problem
from app.modules import load_all_modules
from app.modules.auth import models
from app.modules.auth.permissions import sync_permissions
from app.modules.auth.schemas import clean_email


def _ask(prompt: str) -> str:
    value = input(prompt).strip()
    if not value:
        sys.exit("Không được để trống.")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Tạo tài khoản Admin cao nhất")
    parser.add_argument("--email")
    parser.add_argument("--name")
    parser.add_argument("--generate-password", action="store_true", help="tạo mật khẩu tạm, bắt đổi lần đầu")
    args = parser.parse_args()

    load_all_modules()
    try:
        email = clean_email(args.email or _ask("Email: "))
    except ValueError as error:
        sys.exit(str(error))

    with SessionLocal() as db:
        sync_permissions(db)
        admin_role = db.query(models.Role).filter_by(code="admin").one()
        user = db.query(models.User).filter_by(email=email, deleted_at=None).first()
        if user:
            if admin_role not in user.roles:
                user.roles.append(admin_role)
            db.commit()
            print(f"{email} đã có - đã gán vai trò Admin cao nhất (mật khẩu giữ nguyên).")
            return

        name = args.name or _ask("Họ tên: ")
        temporary = args.generate_password
        if temporary:
            password = secrets.token_urlsafe(9) + "7"
        else:
            password = getpass.getpass("Mật khẩu (tối thiểu 10 ký tự, có chữ và số): ")
            if password != getpass.getpass("Nhập lại mật khẩu: "):
                sys.exit("Hai lần nhập không khớp.")
            problem = password_problem(password)
            if problem:
                sys.exit(problem)

        db.add(models.User(
            email=email, full_name=name, password_hash=hash_password(password),
            must_change_password=temporary, roles=[admin_role],
        ))
        db.commit()
    print(f"Đã tạo Admin cao nhất: {email}. Lần đăng nhập đầu sẽ phải cài 2FA (app Authenticator).")
    if temporary:
        print(f"Mật khẩu tạm (đổi ngay sau khi đăng nhập): {password}")


if __name__ == "__main__":
    main()
