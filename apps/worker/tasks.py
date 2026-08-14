from celery_app import app
from extract import extract_text
from preview import generate_preview


@app.task(name="process_document")
def process_document(document_id: str, file_path: str) -> dict:
    """Extract text (and a preview thumbnail for PDFs) for a stored document."""
    text = extract_text(file_path)

    preview_path = None
    if file_path.lower().endswith(".pdf"):
        preview_path = generate_preview(file_path, output_dir=f"/tmp/previews/{document_id}")

    return {
        "document_id": document_id,
        "text_length": len(text),
        "preview_path": preview_path,
    }
