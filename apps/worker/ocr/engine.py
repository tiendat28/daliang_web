import pytesseract
from PIL import Image


def run_ocr(image_path: str, lang: str = "vie+eng") -> str:
    """Run OCR on an image and return recognized text.

    Requires the `tesseract` binary to be installed on the host/container
    (apt-get install tesseract-ocr tesseract-ocr-vie).
    """
    with Image.open(image_path) as image:
        return pytesseract.image_to_string(image, lang=lang)
