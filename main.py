from fastapi import FastAPI
from routers import router
import logging
from logging.handlers import RotatingFileHandler
log = logging.getLogger()
log.setLevel(logging.INFO)
file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024*5, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
app = FastAPI(
    title="HackRx LLM Query System",
    version="1.0"
)
app.include_router(router.router, prefix="/api/v1")
log.info("Application startup complete.")