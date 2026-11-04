"""File cua bang common.documents: doc noi dung, doi Word sang PDF de xem truoc.

Dung chung cho /api/v1/common/documents (noi bo) va /api/v1/website/public/files
(khach tai MSDS/TDS).
"""
import os
import subprocess
import tempfile
from urllib.parse import quote

from fastapi import HTTPException
from fastapi.responses import FileResponse, Response

from app.core.config import APP_DIR
from app.modules.common import models

# Noi dung file duoc luu thang trong DB (cot documents.content): o dia cua container
# bi xoa sach moi lan deploy lai nen file tung bi mat trong khi ban ghi van con.
# Thu muc duoi chi con de doc nhung file cu da tai len truoc day.
LEGACY_UPLOAD_DIR = str(APP_DIR / "uploads")

# Trinh duyet khong render duoc file Word, nen convert sang PDF (LibreOffice headless) de xem truoc.
# Ban PDF nay tao lai duoc bat cu luc nao nen de o thu muc tam.
PDF_CACHE_DIR = os.path.join(tempfile.gettempdir(), "daliang_pdf_cache")
os.makedirs(PDF_CACHE_DIR, exist_ok=True)

OFFICE_MIME_TYPES = {
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
OFFICE_EXTENSIONS = {".doc", ".docx"}

def is_office_document(doc: models.Document) -> bool:
    ext = os.path.splitext(doc.stored_filename)[1].lower()
    return ext in OFFICE_EXTENSIONS or doc.mime_type in OFFICE_MIME_TYPES


def legacy_path(doc: models.Document) -> str:
    return os.path.join(LEGACY_UPLOAD_DIR, doc.stored_filename)


def document_bytes(doc: models.Document) -> bytes:
    if doc.content:
        return doc.content
    # Tai lieu tai len truoc khi chuyen sang luu trong DB
    path = legacy_path(doc)
    if os.path.exists(path):
        with open(path, "rb") as src:
            return src.read()
    raise HTTPException(404, "File không còn trên máy chủ, vui lòng tải lên lại")


def pdf_cache_path(stored_filename: str) -> str:
    return os.path.join(PDF_CACHE_DIR, f"{os.path.splitext(stored_filename)[0]}.pdf")


def convert_to_pdf(data: bytes, stored_filename: str) -> str:
    pdf_path = pdf_cache_path(stored_filename)
    if os.path.exists(pdf_path):
        return pdf_path

    src_path = os.path.join(PDF_CACHE_DIR, stored_filename)
    with open(src_path, "wb") as out:
        out.write(data)
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", PDF_CACHE_DIR, src_path],
            check=True,
            timeout=60,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise HTTPException(502, "Không thể tạo bản xem trước cho tài liệu Word") from exc
    finally:
        if os.path.exists(src_path):
            os.remove(src_path)

    if not os.path.exists(pdf_path):
        raise HTTPException(502, "Không thể tạo bản xem trước cho tài liệu Word")
    return pdf_path


def document_response(doc: models.Document, inline: bool = False):
    """Tra file ve trinh duyet. inline + file Word thi tra ban PDF de xem ngay."""
    data = document_bytes(doc)

    if inline and is_office_document(doc):
        pdf_path = convert_to_pdf(data, doc.stored_filename)
        pdf_name = f"{os.path.splitext(doc.original_filename or doc.stored_filename)[0]}.pdf"
        return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_name, content_disposition_type="inline")

    filename = doc.original_filename or doc.stored_filename
    disposition = "inline" if inline else "attachment"
    return Response(
        content=data,
        media_type=doc.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f"{disposition}; filename*=UTF-8''{quote(filename)}"},
    )


def remove_cached_files(doc: models.Document) -> None:
    """Xoa file cu tren dia (neu con) va ban PDF xem truoc, truoc khi xoa ban ghi."""
    for path in (legacy_path(doc), pdf_cache_path(doc.stored_filename)):
        if os.path.exists(path):
            os.remove(path)
