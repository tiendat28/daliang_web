import os

from pdf2image import convert_from_path


def generate_preview(pdf_path: str, output_dir: str, dpi: int = 100) -> str:
    """Render the first page of a PDF to a PNG thumbnail and return its path.

    Requires the `poppler` binary to be installed on the host/container
    (apt-get install poppler-utils).
    """
    os.makedirs(output_dir, exist_ok=True)
    pages = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
    output_path = os.path.join(output_dir, "preview.png")
    pages[0].save(output_path, "PNG")
    return output_path
