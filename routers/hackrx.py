from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from services.pdf_loader import extract_text_from_pdf
from services.chunker import chunk_text
from services.pinecone_manager import index_chunks, query_chunks, check_if_indexed
from services.llm_answerer import generate_answer
from fastapi.concurrency import run_in_threadpool
import asyncio
import hashlib
router = APIRouter()
class QueryRequest(BaseModel):
    documents: str
    questions: list[str]
@router.post("/hackrx/run")
async def run_submission(payload: QueryRequest):
    try:
        document_url = payload.documents
        namespace = hashlib.sha256(document_url.encode()).hexdigest()
        is_indexed = await run_in_threadpool(check_if_indexed, namespace)
        if not is_indexed:
            print(f"Indexing document for namespace: {namespace}", flush=True)
            text = await run_in_threadpool(extract_text_from_pdf, document_url)
            chunks = await run_in_threadpool(chunk_text, text)
            await run_in_threadpool(index_chunks, chunks, namespace)
            print("Indexing complete.", flush=True)
        else:
            print(f"Document already exists. Skipping indexing.", flush=True)
        semaphore = asyncio.Semaphore(7)
        async def get_single_answer(question: str, ns: str):
            async with semaphore:
                print(f"Processing question: {question}", flush=True)
                context = await run_in_threadpool(query_chunks, question, ns)
                answer, rationale = await run_in_threadpool(generate_answer, question, context)
                return {"question": question, "answer": answer, "rationale": rationale}
        tasks = [get_single_answer(question, namespace) for question in payload.questions]
        results = await asyncio.gather(*tasks)
        final_answers = [result["answer"] for result in results]
        return {"answers": final_answers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
