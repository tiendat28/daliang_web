"""Gui email qua Resend (HTTPS API) - Railway chan cong SMTP nen khong dung SMTP.

Chua dat RESEND_API_KEY thi khong gui ma in noi dung ra log: van thu duoc luong
quen mat khau tren may minh (lay link trong `docker compose logs backend`).
"""
import logging

import httpx

from app.core.config import settings

log = logging.getLogger("daliang.mail")
RESEND_URL = "https://api.resend.com/emails"


def send_email(to: str, subject: str, html: str, text: str) -> bool:
    """True neu da gui (hoac da in ra log khi chua cau hinh). Loi mang khong lam do request."""
    if not settings.resend_api_key:
        log.warning("[mail chua cau hinh] Gui toi %s - %s\n%s", to, subject, text)
        print(f"[mail chua cau hinh] Gui toi {to} - {subject}\n{text}", flush=True)
        return True
    try:
        response = httpx.post(
            RESEND_URL,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={"from": settings.mail_from, "to": [to], "subject": subject, "html": html, "text": text},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError as error:
        log.error("Gui email toi %s that bai: %s", to, error)
        return False
