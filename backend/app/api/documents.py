import os
import shutil
import subprocess
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models, schemas

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Trinh duyet khong render duoc file Word, nen convert sang PDF (LibreOffice headless) de xem truoc
PDF_CACHE_DIR = os.path.join(UPLOAD_DIR, "pdf_cache")
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


def _convert_to_pdf(src_path: str, stored_filename: str) -> str:
    pdf_path = os.path.join(PDF_CACHE_DIR, f"{os.path.splitext(stored_filename)[0]}.pdf")
    if os.path.exists(pdf_path):
        return pdf_path
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", PDF_CACHE_DIR, src_path],
            check=True,
            timeout=60,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise HTTPException(502, "Khong the tao ban xem truoc cho tai lieu Word") from exc
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
    ext = os.path.splitext(file.filename or "")[1]
    stored_filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, stored_filename)
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    doc = models.Document(
        category=category,
        name=name.strip() or file.filename,
        original_filename=file.filename,
        stored_filename=stored_filename,
        mime_type=file.content_type,
        file_size=os.path.getsize(dest_path),
        uploaded_by=uploaded_by.strip(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{document_id}/file")
def get_document_file(document_id: int, inline: bool = False, db: Session = Depends(get_db)):
    doc = _get_or_404(db, document_id)
    path = os.path.join(UPLOAD_DIR, doc.stored_filename)
    if not os.path.exists(path):
        raise HTTPException(404, "File khong ton tai tren server")

    if inline and _is_office_document(doc):
        pdf_path = _convert_to_pdf(path, doc.stored_filename)
        pdf_name = f"{os.path.splitext(doc.original_filename or doc.stored_filename)[0]}.pdf"
        return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_name, content_disposition_type="inline")

    return FileResponse(
        path,
        media_type=doc.mime_type or "application/octet-stream",
        filename=doc.original_filename,
        content_disposition_type="inline" if inline else "attachment",
    )


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = _get_or_404(db, document_id)
    path = os.path.join(UPLOAD_DIR, doc.stored_filename)
    if os.path.exists(path):
        os.remove(path)
    pdf_path = os.path.join(PDF_CACHE_DIR, f"{os.path.splitext(doc.stored_filename)[0]}.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    db.delete(doc)
    db.commit()
    return {"ok": True}
