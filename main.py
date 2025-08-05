from fastapi import FastAPI
from routers import hackrx

app = FastAPI(
    title="HackRx LLM Query System",
    version="1.0"
)

app.include_router(hackrx.router, prefix="/api/v1")
