from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from services.pdf_loader import extract_text_from_pdf
# from services.chunker import chunk_text
# from services.pinecone_manager import index_chunks, query_chunks
# from services.llm_answerer import generate_answer

router = APIRouter()

# class QueryRequest(BaseModel):
#     documents: str
#     questions: list[str]

@router.post("/hackrx/run")
# async def run_submission(payload: QueryRequest):
async def run_submission():
    try:
        # text = extract_text_from_pdf(payload.documents)
        # chunks = chunk_text(text)
        # index_chunks(chunks)

        # answers = []
        # for question in payload.questions:
        #     context = query_chunks(question)
        #     answer = generate_answer(question, context)
        #     answers.append(answer)

        return {"answers": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
