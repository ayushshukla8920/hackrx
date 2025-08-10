import os
import requests
import mimetypes
from services.pdf_loader import extract_text_from_pdf
from pptx import Presentation
from openpyxl import load_workbook
from PIL import Image
import pytesseract
import io
import logging
from docx import Document
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
    wb = load_workbook(io.BytesIO(response.content), read_only=True)
    all_sheets_text = []
    for sheet in wb.worksheets:
        headers = []
        header_row_index = -1
        for i, row in enumerate(sheet.iter_rows()):
            potential_headers = [str(cell.value) for cell in row if cell.value is not None]
            if len(potential_headers) > 1:
                headers = potential_headers
                header_row_index = i + 1
                logger.info(f"Found header row at index {header_row_index} in sheet '{sheet.title}'")
                break
        if not headers:
            logger.warning(f"Could not find a valid header row in sheet '{sheet.title}'. Skipping.")
            continue
        for row in sheet.iter_rows(min_row=header_row_index + 1):
            row_data = []
            for header, cell in zip(headers, row):
                if cell.value is not None:
                    row_data.append(f"{header} is {cell.value}")
            if row_data:
                all_sheets_text.append("Record: " + ", ".join(row_data) + ".")
    return "\n".join(all_sheets_text)
def extract_text_from_image(file_url: str) -> str:
    response = requests.get(file_url)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content))
    text = pytesseract.image_to_string(img)
    return text
def extract_text_from_docx(file_url: str) -> str:
    response = requests.get(file_url)
    response.raise_for_status()
    document = Document(io.BytesIO(response.content))
    text = []
    for paragraph in document.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)
def extract_text_from_file(file_url: str) -> str:
    logger.info(f"Downloading file from {file_url}")
    url_path = file_url.split('?')[0]
    file_extension = os.path.splitext(url_path)[1].lower()
    file_type, _ = mimetypes.guess_type(file_url)
    if file_type == 'application/pdf' or file_extension == '.pdf':
        return extract_text_from_pdf(file_url)
    elif file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation' or file_extension == '.pptx':
        return extract_text_from_pptx(file_url)
    elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file_extension in ('.docx', '.doc'):
        return extract_text_from_docx(file_url)
    elif file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or file_extension in ('.xlsx', '.xls'):
        return extract_text_from_xlsx(file_url)
    elif file_type and file_type.startswith('image/') or file_extension in ('.jpeg', '.jpg', '.png'):
        return extract_text_from_image(file_url)
    else:
        return "No content Found in Files"