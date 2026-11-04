from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent.parent
# Font + logo cua to phieu in, phuc vu qua /api/v1/static
STATIC_DIR = APP_DIR / "static"

# Moi API cua ca he thong nam duoi tien to nay: /api/v1/<module>/...
API_PREFIX = "/api/v1"

DEV_JWT_SECRET = "dev-chi-dung-tren-may-minh-doi-khi-trien-khai"


class Settings(BaseSettings):
    """Doc tu bien moi truong (ten viet hoa, vd DATABASE_URL, JWT_SECRET)."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://labuser:labpass@db:5432/labdb"
    # Portal va website goi API cung ten mien (nginx / proxy Vite / Vercel rewrite)
    # nen mac dinh khong mo CORS cho ai.
    cors_origins: list[str] = []

    # ---- Dang nhap ----
    jwt_secret: str = DEV_JWT_SECRET
    access_token_minutes: int = 15
    remember_days: int = 30             # tick "Ghi nho thiet bi": phien song 30 ngay
    session_hours: int = 12             # khong tick: cookie mat khi tat trinh duyet, toi da 12 gio
    # True khi chay HTTPS (Vercel/Railway) - cookie chi gui qua HTTPS
    cookie_secure: bool = False
    login_max_attempts: int = 5         # sai lien tiep bao nhieu lan thi khoa tam
    login_lock_minutes: int = 15
    password_reset_minutes: int = 30
    totp_issuer: str = "Daliang VN"
    # Tạm ẩn 2FA trong giai đoạn đầu; giữ nguyên model/API để bật lại bằng env.
    two_factor_enabled: bool = False

    # ---- Email (quen mat khau) - Resend, goi qua HTTPS vi Railway chan SMTP ----
    resend_api_key: str = ""            # de trong: khong gui, in link ra log (de test)
    mail_from: str = "Daliang VN <noreply@daliang.com>"
    portal_url: str = "http://localhost:5173"   # goc URL cua cong noi bo, de ghep link dat lai MK

    @field_validator("database_url")
    @classmethod
    def _sqlalchemy_scheme(cls, value: str) -> str:
        # Railway/Heroku cap URL dang postgres://, SQLAlchemy 2 chi nhan postgresql://
        # Su dung postgresql+psycopg2:// de tranh xung dot driver psycopg v3 / psycopg2
        if value.startswith("postgres://"):
            value = "postgresql+psycopg2://" + value[len("postgres://"):]
        elif value.startswith("postgresql://"):
            value = "postgresql+psycopg2://" + value[len("postgresql://"):]
        return value

    @field_validator("jwt_secret")
    @classmethod
    def _default_when_blank(cls, value: str) -> str:
        return value or DEV_JWT_SECRET   # compose truyen chuoi rong khi .env chua dat


settings = Settings()
