from enum import Enum
from pydantic import BaseModel, Field, field_validator


class NewsCategory(str, Enum):
    WORLD = "World"
    SPORTS = "Sports"
    BUSINESS = "Business"
    SCI_TECH = "Sci/Tech"


class NewsClassification(BaseModel):
    category: NewsCategory
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""

    @field_validator("reasoning")
    @classmethod
    def trim_reasoning(cls, v):
        return v[:200]