# ...existing code...

import requests
import io
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_url: str) -> str:
	"""
	Downloads a PDF from a URL and extracts its text content.
	"""
	response = requests.get(pdf_url)
	response.raise_for_status()
	pdf_file = io.BytesIO(response.content)
	reader = PdfReader(pdf_file)
	text = ""
	for page in reader.pages:
		text += page.extract_text() or ""
	return text
    
# ...more existing code...
