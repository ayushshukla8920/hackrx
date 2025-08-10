from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from services.file_loader import extract_text_from_file
from services.agentic_workflow import handle_agentic_workflow
from services.chunker import chunk_text, clean_text
from services.vectordb_manager import index_chunks, query_chunks, check_if_indexed
from services.llm_answerer import generate_answer
from fastapi.concurrency import run_in_threadpool
import asyncio
import hashlib
import logging
logger = logging.getLogger(__name__)
router = APIRouter()
class QueryRequest(BaseModel):
    documents: str
    questions: list[str]
@router.post("/hackrx/run")
async def run_submission(payload: QueryRequest, request: Request):
    auth_header = request.headers.get("authorization")
    logger.info(f"Authorization header: {auth_header}")
    try:
        document_url = payload.documents
        namespace = hashlib.sha256(document_url.encode()).hexdigest()
        is_indexed = await run_in_threadpool(check_if_indexed, namespace)
        logger.info(f"Received new request for document: {payload.documents}")
        logger.info(f"Number of questions received: {len(payload.questions)}")
        if not is_indexed:
            logger.info(f"Indexing document for namespace: {namespace}")
            text = await run_in_threadpool(extract_text_from_file, document_url)
            cleaned_text = clean_text(text)
            chunks = await run_in_threadpool(chunk_text, cleaned_text)
            await run_in_threadpool(index_chunks, chunks, namespace)
            logger.info("Indexing complete.")
        else:
            logger.info(f"Document already exists. Skipping indexing.")
        semaphore = asyncio.Semaphore(7)
        async def get_single_answer(question: str, ns: str):
            async with semaphore:
                logger.info(f"Processing question: {question}")
                context = await run_in_threadpool(query_chunks, question, ns)
                answer, rationale = await run_in_threadpool(generate_answer, question, context)
                if(answer == "handle_agentic_workflow()"):
                    logger.info("Handling agentic workflow for question.")
                    answer = await handle_agentic_workflow(document_url, question)
                return {"question": question, "answer": answer, "rationale": rationale}
        tasks = [get_single_answer(question, namespace) for question in payload.questions]
        results = await asyncio.gather(*tasks)
        final_answers = [result["answer"] for result in results]
        logger.info("All questions processed successfully.")
        logger.debug(f"Final answers: {final_answers}")
        return {"answers": final_answers}
    except Exception as e:
        logger.error(f"An error occurred while processing document {payload.documents}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
