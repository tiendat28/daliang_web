import os
import subprocess
import tempfile
import uuid
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas

# Noi dung file duoc luu thang trong DB (cot documents.content): o dia cua container
# bi xoa sach moi lan deploy lai nen file tung bi mat trong khi ban ghi van con.
# Thu muc duoi chi con de doc nhung file cu da tai len truoc day.
LEGACY_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

# Trinh duyet khong render duoc file Word, nen convert sang PDF (LibreOffice headless) de xem truoc.
# Ban PDF nay tao lai duoc bat cu luc nao nen de o thu muc tam.
PDF_CACHE_DIR = os.path.join(tempfile.gettempdir(), "daliang_pdf_cache")
os.makedirs(PDF_CACHE_DIR, exist_ok=True)

OFFICE_MIME_TYPES = {
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
OFFICE_EXTENSIONS = {".doc", ".docx"}

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _is_office_document(doc: models.Document) -> bool:
    ext = os.path.splitext(doc.stored_filename)[1].lower()
    return ext in OFFICE_EXTENSIONS or doc.mime_type in OFFICE_MIME_TYPES


def _legacy_path(doc: models.Document) -> str:
    return os.path.join(LEGACY_UPLOAD_DIR, doc.stored_filename)


def _document_bytes(doc: models.Document) -> bytes:
    if doc.content:
        return doc.content
    # Tai lieu tai len truoc khi chuyen sang luu trong DB
    path = _legacy_path(doc)
    if os.path.exists(path):
        with open(path, "rb") as src:
            return src.read()
    raise HTTPException(404, "File khong con tren server, vui long tai len lai")


def _pdf_cache_path(stored_filename: str) -> str:
    return os.path.join(PDF_CACHE_DIR, f"{os.path.splitext(stored_filename)[0]}.pdf")


def _convert_to_pdf(data: bytes, stored_filename: str) -> str:
    pdf_path = _pdf_cache_path(stored_filename)
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
        raise HTTPException(502, "Khong the tao ban xem truoc cho tai lieu Word") from exc
    finally:
        if os.path.exists(src_path):
            os.remove(src_path)

    if not os.path.exists(pdf_path):
        raise HTTPException(502, "Khong the tao ban xem truoc cho tai lieu Word")
    return pdf_path


def _get_or_404(db: Session, document_id: int) -> models.Document:
    doc = db.query(models.Document).get(document_id)
    if not doc:
        raise HTTPException(404, "Khong tim thay tai lieu")
    return doc


@router.get("", response_model=list[schemas.DocumentOut])
def list_documents(category: models.DocumentCategory | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Document)
    if category:
        query = query.filter(models.Document.category == category)
    return query.order_by(models.Document.uploaded_at.desc()).all()


@router.post("", response_model=schemas.DocumentOut)
def upload_document(
    category: models.DocumentCategory = Form(...),
    name: str = Form(...),
    uploaded_by: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    data = file.file.read()
    if not data:
        raise HTTPException(400, "File rong")

    ext = os.path.splitext(file.filename or "")[1]
    doc = models.Document(
        category=category,
        name=name.strip() or file.filename,
        original_filename=file.filename,
        stored_filename=f"{uuid.uuid4().hex}{ext}",
        content=data,
        mime_type=file.content_type,
        file_size=len(data),
        uploaded_by=uploaded_by.strip(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{document_id}/file")
def get_document_file(document_id: int, inline: bool = False, db: Session = Depends(get_db)):
    doc = _get_or_404(db, document_id)
    data = _document_bytes(doc)

    if inline and _is_office_document(doc):
        pdf_path = _convert_to_pdf(data, doc.stored_filename)
        pdf_name = f"{os.path.splitext(doc.original_filename or doc.stored_filename)[0]}.pdf"
        return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_name, content_disposition_type="inline")

    filename = doc.original_filename or doc.stored_filename
    disposition = "inline" if inline else "attachment"
    return Response(
        content=data,
        media_type=doc.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f"{disposition}; filename*=UTF-8''{quote(filename)}"},
    )


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = _get_or_404(db, document_id)
    for path in (_legacy_path(doc), _pdf_cache_path(doc.stored_filename)):
        if os.path.exists(path):
            os.remove(path)
    db.delete(doc)
    db.commit()
    return {"ok": True}
