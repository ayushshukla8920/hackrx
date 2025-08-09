import requests
import mimetypes
from services.pdf_loader import extract_text_from_pdf
from pptx import Presentation
from openpyxl import load_workbook
from PIL import Image
import pytesseract
import io
import logging
logger = logging.getLogger(__name__)
def extract_text_from_pptx(file_url: str) -> str:
    response = requests.get(file_url)
    response.raise_for_status()
    prs = Presentation(io.BytesIO(response.content))
    text = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text.append(shape.text)
    return "\n".join(text)
def extract_text_from_xlsx(file_url: str) -> str:
    response = requests.get(file_url)
    response.raise_for_status()
    wb = load_workbook(io.BytesIO(response.content))
    text = []
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value:
                    text.append(str(cell.value))
    return " ".join(text)
def extract_text_from_image(file_url: str) -> str:
    response = requests.get(file_url)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content))
    text = pytesseract.image_to_string(img)
    return text
def extract_text_from_file(file_url: str) -> str:
    logger.info(f"Downloading file from {file_url}")
    file_type, _ = mimetypes.guess_type(file_url)
    logger.info(f"Detected file type: {file_type}")
    if not file_type:
        if file_url.endswith('.pdf'):
            file_type = 'application/pdf'
        elif file_url.endswith('.pptx'):
            file_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        elif file_url.endswith('.xlsx'):
            file_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif file_url.endswith(('.jpeg', '.jpg', '.png')):
            file_type = 'image/jpeg'
    if file_type == 'application/pdf':
        return extract_text_from_pdf(file_url)
    elif file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        return extract_text_from_pptx(file_url)
    elif file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return extract_text_from_xlsx(file_url)
    elif file_type and file_type.startswith('image/'):
        return extract_text_from_image(file_url)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")