
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from services.pdf_loader import extract_text_from_pdf
from services.chunker import chunk_text
from services.pinecone_manager import index_chunks, query_chunks
from services.llm_answerer import generate_answer


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
        text = extract_text_from_pdf(payload.documents)
        # Step 2: Chunk the text
        chunks = chunk_text(text)
        # Step 3: Index chunks in Pinecone
        index_chunks(chunks)

        answers = []
        for question in payload.questions:
            # Step 4: Retrieve relevant context
            context = query_chunks(question)
            # Step 5: Generate answer and rationale
            answer, rationale = generate_answer(question, context)
            answers.append({"answer": answer, "rationale": rationale})

        return {"answers": answers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

