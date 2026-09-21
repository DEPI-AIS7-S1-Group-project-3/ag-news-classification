from fastapi import APIRouter, HTTPException
from app.schemas.news import NewsPredictionRequest, NewsPredictionResponse, NewsExtractionResponse
from app.services.run_pipeline import run_pipeline
from app.pipeline.retry import extract_with_retry
from app.pipeline.errors import PipelineError

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

@router.post("/extract", response_model=NewsExtractionResponse)
def extract_news_info(payload: NewsPredictionRequest):
    try:
        result = extract_with_retry(payload.text)
        return NewsExtractionResponse(
            topic_keywords=result.topic_keywords,
            entities=result.entities,
            summary=result.summary,
            sentiment=result.sentiment.value,
            is_breaking_news=result.is_breaking_news,
        )
    except PipelineError as e:
        raise HTTPException(status_code=500, detail=str(e))