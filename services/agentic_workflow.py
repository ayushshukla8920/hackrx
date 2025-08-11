import requests
import io
import re
import fitz
from bs4 import BeautifulSoup
import logging
import json
from .llm_answerer import model
from .fetch import fetch_url_content
logger = logging.getLogger(__name__)
async def handle_agentic_workflow(document_url: str, question: str) -> str:
    extracted_text = await fetch_url_content(document_url)
    prompt = f"""You are an expert Agent in extracting and answering questions based on the content of documents. Your task is to provide a precise answer to the user's question based on the provided context.If you need to access a webpage or make a further api call then reply only with string "<agent>fetch_url_content(),url to be called</agent>" to trigger the function.
    CONTEXT:
    ---
    {extracted_text}
    ---

    QUESTION: {question}
    
    Amswer:"""
    logger.info("AGENT: Sending final prompt to LLM for a precise answer.")
    try:
        llm_response = "<agent>fetch_url_content(),{document_url}</agent>"
        match = re.search(r"<agent>(.*?)</agent>", llm_response)
        instruction = match.group(1)
        logger.info(f"AGENT: Instruction extracted: {instruction}")
        extracted_text = await fetch_url_content(document_url)
        llm_response = await model.generate_content_async(prompt)
        while("<agent>" in llm_response.text.strip()):
            match = re.search(r"<agent>(.*?)</agent>", llm_response.text.strip())
            instruction = match.group(1).split(",")[1]
            logger.info(f"AGENT: Instruction extracted: {instruction}")
            data = await fetch_url_content(instruction)
            newprompt = prompt+ "Information extracted from  "+ instruction + " : " + data + "\nIf the Required into is in the context then return it elsen Proceed for the Next Step if needed else if you can derive the answer to question from this info then return onlt the answer :  "
            logger.info(newprompt)
            llm_response = await model.generate_content_async(newprompt)
        return llm_response.text.strip()
    except Exception as e:
        logger.error(f"AGENT: The final LLM call failed: {e}", exc_info=True)
        return "Error: The language model failed to generate a final answer."