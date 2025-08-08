import requests
import io
import fitz  # PyMuPDF library
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_url: str) -> str:
    """
    Downloads a PDF from a URL and extracts its text using the fast PyMuPDF library.
    """
    logger.info("Downloading PDF")
    try:
        response = requests.get(pdf_url)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Use a 'with' statement for safer file handling
        with fitz.open(stream=response.content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text() or ""
        
        logger.info("PDF text extraction complete.")
        return text
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download PDF from {pdf_url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to process PDF: {e}")
        raise