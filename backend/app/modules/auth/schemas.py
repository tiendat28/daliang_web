"""Du lieu vao/ra cua dang nhap."""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


def clean_email(value: str) -> str:
    value = value.strip().lower()
    if "@" not in value or len(value) > 150:
        raise ValueError("Email không hợp lệ")
    return value


class LoginIn(BaseModel):
    identifier: str = Field(min_length=1, max_length=150)   # email hoac ma nhan vien
    password: str = Field(min_length=1, max_length=200)
    remember: bool = False                                  # "Ghi nho thiet bi nay trong 30 ngay"

    @field_validator("identifier")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return value.strip().lower()


class CodeIn(BaseModel):
    code: str = Field(min_length=6, max_length=20)   # ma TOTP 6 so hoac ma du phong XXXX-XXXX


class PasswordIn(BaseModel):
    password: str = Field(min_length=1, max_length=200)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=1, max_length=200)


class ForgotPasswordIn(BaseModel):
    email: str

    _email = field_validator("email")(clean_email)


class ResetPasswordIn(BaseModel):
    token: str = Field(min_length=10, max_length=200)
    new_password: str = Field(min_length=1, max_length=200)


class RoleBrief(BaseModel):
    code: str
    name: str


class MeOut(BaseModel):
    id: int
    email: str
    employee_code: Optional[str] = None
    department: Optional[str] = None
    full_name: str
    roles: List[RoleBrief]
    permissions: List[str]            # "*" = moi quyen
    totp_enabled: bool
    require_2fa: bool
    must_change_password: bool


class LoginOut(BaseModel):
    """step: done = da vao; verify_2fa = nhap ma; setup_2fa = vai tro bat buoc 2FA nhung chua cai."""
    step: Literal["done", "verify_2fa", "setup_2fa"]
    user: Optional[MeOut] = None


class TotpSetupOut(BaseModel):
    qr: str          # data URI anh SVG
    secret: str      # nhap tay neu khong quet duoc QR


class BackupCodesOut(BaseModel):
    backup_codes: List[str]
    user: Optional[MeOut] = None     # co khi bat 2FA ngay luc dang nhap -> vao luon
