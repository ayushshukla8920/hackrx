import requests
import io
import re
import fitz
from bs4 import BeautifulSoup
import logging
import json
logger = logging.getLogger(__name__)
async def fetch_url_content(url: str) -> str:
    extracted_text = ""
    try:
        logger.info(f"AGENT: Differentiating and extracting content from {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=20, stream=True)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' in content_type:
            logger.info("AGENT: Identified document as PDF. Processing...")
            pdf_content = response.content
            with fitz.open(stream=pdf_content, filetype="pdf") as doc:
                extracted_text = "".join(page.get_text() for page in doc)
        elif 'text/html' in content_type:
            logger.info("AGENT: Identified document as a webpage. Processing...")
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            extracted_text = soup.body.get_text(separator='\\n', strip=True)
        elif 'application/json' in content_type:
            logger.info("AGENT: Identified document as JSON. Processing...")
            try:
                json_data = response.json()
                extracted_text = json.dumps(json_data, indent=2)
            except json.JSONDecodeError:
                logger.warning("AGENT: Content-Type was JSON, but failed to parse. Falling back to raw text.")
                extracted_text = response.text
        else:
            logger.warning(f"AGENT: Unknown content type '{content_type}'. Attempting to process as a webpage.")
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            extracted_text = soup.body.get_text(separator='\\n', strip=True)
        if not extracted_text.strip():
            return "The document was processed, but no text content could be extracted."
    except requests.exceptions.RequestException as e:
        logger.error(f"AGENT: Failed to download or access {document_url}: {e}")
        return f"Error: Failed to download or access the document at the specified URL."
    except Exception as e:
        logger.error(f"AGENT: An error occurred during text extraction: {e}", exc_info=True)
        return f"Error: An unexpected error occurred while processing the document."
    logger.info(extracted_text[:500] + "...")
    return extracted_text