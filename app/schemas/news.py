from pydantic import BaseModel, Field


class NewsPredictionRequest(BaseModel):
    text: str = Field(
        ..., example="Apple reveals new M-series chips in latest event."
    )


class NewsPredictionResponse(BaseModel):
    category: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    used_fallback: bool = False

class NewsExtractionResponse(BaseModel):
    topic_keywords: list[str]
    entities: list[str]
    summary: str
    sentiment: str
    is_breaking_news: bool