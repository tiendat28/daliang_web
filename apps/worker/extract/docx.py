from docx import Document


def extract_text(path: str) -> str:
    document = Document(path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)
