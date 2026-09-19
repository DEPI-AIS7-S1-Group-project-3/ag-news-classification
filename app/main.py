from fastapi import FastAPI
from app.core.config import settings
from app.api.routes_news import router as news_router
from app.core.logging import setup_logging
setup_logging()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AG News Classification API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include News Classification Router
app.include_router(news_router, prefix=settings.API_V1_STR, tags=["News Classification"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AG News Classification API", "status": "running"}