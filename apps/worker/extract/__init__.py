from .docx import extract_text as extract_text_docx
from .pdf import extract_text as extract_text_pdf
from .xlsx import extract_text as extract_text_xlsx

__all__ = ["extract_text_pdf", "extract_text_docx", "extract_text_xlsx"]


def extract_text(path: str) -> str:
    """Dispatch to the right extractor based on file extension."""
    suffix = path.rsplit(".", 1)[-1].lower()
    if suffix == "pdf":
        return extract_text_pdf(path)
    if suffix == "docx":
        return extract_text_docx(path)
    if suffix in ("xlsx", "xlsm"):
        return extract_text_xlsx(path)
    raise ValueError(f"Unsupported file type: {suffix}")
