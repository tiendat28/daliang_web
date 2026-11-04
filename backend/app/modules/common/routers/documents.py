import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, defer

from app.core.crud import get_or_404
from app.core.database import get_db
from app.modules.common import models, schemas
from app.modules.common.services.documents import document_response, remove_cached_files

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[schemas.DocumentOut])
def list_documents(category: models.DocumentCategory | None = None, db: Session = Depends(get_db)):
    # Khong nap cot content (noi dung file) khi chi can danh sach
    query = db.query(models.Document).options(defer(models.Document.content))
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
        raise HTTPException(400, "File rỗng")

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
    doc = get_or_404(db, models.Document, document_id, "Không tìm thấy tài liệu")
    return document_response(doc, inline=inline)


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = get_or_404(db, models.Document, document_id, "Không tìm thấy tài liệu")
    remove_cached_files(doc)
    db.delete(doc)
    db.commit()
    return {"ok": True}
