import requests
import io
import fitz
import logging
logger = logging.getLogger(__name__)
def extract_text_from_pdf(pdf_url: str) -> str:
    logger.info("Downloading PDF")
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        logger.info("Downloading Done, processing PDF")
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