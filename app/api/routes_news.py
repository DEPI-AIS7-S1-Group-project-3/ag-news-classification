from fastapi import APIRouter
from app.schemas.news import NewsPredictionRequest, NewsPredictionResponse
from app.services.run_pipeline import run_pipeline

router = APIRouter()


@router.get("/status")
def news_route_status():
    return {"message": "News classification routes are working!"}


@router.post("/predict", response_model=NewsPredictionResponse)
def predict_news_category(payload: NewsPredictionRequest):
    result = run_pipeline(payload.text)
    return NewsPredictionResponse(
        category=result["category"],
        confidence=result["confidence"],
        used_fallback=result["used_fallback"],
    )