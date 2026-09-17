from pydantic import BaseModel, Field


class NewsPredictionRequest(BaseModel):
    text: str = Field(..., example="Apple reveals new M-series chips in latest event.")


class NewsPredictionResponse(BaseModel):
    category: str
    confidence: float | None = None