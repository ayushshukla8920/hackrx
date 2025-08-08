from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from services.pdf_loader import extract_text_from_pdf
from services.chunker import chunk_text
from services.pinecone_manager import index_chunks, query_chunks
from services.llm_answerer import generate_answer
from fastapi.concurrency import run_in_threadpool

router = APIRouter()

class QueryRequest(BaseModel):
    documents: str  # Document URL
    questions: list[str]

@router.get("/", response_class=HTMLResponse)
async def testendpoint():
    return "<h1>LLM Query System</h1><br />All Systems are Working"

@router.post("/hackrx/run")
async def run_submission(payload: QueryRequest):
    try:
        # Step 1: Extract text from document (PDF, DOCX, etc.)
        text = await run_in_threadpool(extract_text_from_pdf, payload.documents)
        print("Text extracted", flush=True)

        # Step 2: Chunk the text
        # chunks = await run_in_threadpool(chunk_text, text)
        # print("Text chunked", flush=True)

        # # Step 3: Index chunks in Pinecone
        # await run_in_threadpool(index_chunks, chunks)
        # print("Chunks indexed", flush=True)

        # answers = []
        # for question in payload.questions:
        #     # Step 4: Retrieve relevant context
        #     context = await run_in_threadpool(query_chunks, question)
        #     print(f"Context retrieved for: {question}", flush=True)

        #     # Step 5: Generate answer and rationale
        #     answer, rationale = await run_in_threadpool(generate_answer, question, context)
        #     print(f"Answer generated for: {question}", flush=True)

        #     answers.append({"answer": answer, "rationale": rationale})

        return {"answers": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
