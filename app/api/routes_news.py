from fastapi import APIRouter
from app.schemas.news import NewsPredictionRequest, NewsPredictionResponse

router = APIRouter()


@router.get("/status")
def news_route_status():
    return {"message": "News classification routes are working!"}


@router.post("/predict", response_model=NewsPredictionResponse)
def predict_news_category(payload: NewsPredictionRequest):
    # TODO: Integrate Groq API or HuggingFace Model Pipeline here
    return NewsPredictionResponse(category="Sci/Tech", confidence=0.95)