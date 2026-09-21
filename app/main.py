from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Mount static files to serve the frontend directory
app.mount("/static", StaticFiles(directory="app/frontend"), name="static")

@app.get("/")
def read_root():
    return FileResponse("app/frontend/index.html")