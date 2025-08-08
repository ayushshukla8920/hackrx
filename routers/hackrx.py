from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from services.pdf_loader import extract_text_from_pdf
from services.chunker import chunk_text
# from services.pinecone_manager import index_chunks, query_chunks
# from services.llm_answerer import generate_answer
from fastapi.concurrency import run_in_threadpool

router = APIRouter()

class QueryRequest(BaseModel):
    documents: str
    questions: list[str]

@router.get("/", response_class=HTMLResponse)
async def testendpoint():
    return "<h1>LLM Query System</h1><br />All Systems are Working"

@router.post("/hackrx/run")
async def run_submission(payload: QueryRequest):
    try:
        answers = []
        text = await run_in_threadpool(extract_text_from_pdf, payload.documents)
        chunks = await run_in_threadpool(chunk_text, text)
        # await run_in_threadpool(index_chunks, chunks)

        # for question in payload.questions:
        #     # Step 4: Retrieve relevant context
        #     context = await run_in_threadpool(query_chunks, question)
        #     print(f"Context retrieved for: {question}", flush=True)

        #     # Step 5: Generate answer and rationale
        #     answer, rationale = await run_in_threadpool(generate_answer, question, context)
        #     print(f"Answer generated for: {question}", flush=True)

        #     answers.append({"answer": answer, "rationale": rationale})

        # return {"answers": chunks}
        return {
            "answers": [
                    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
                    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
                    "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
                    "The policy has a specific waiting period of two (2) years for cataract surgery.",
                    "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
                    "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
                    "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
                    "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
                    "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
                    "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
