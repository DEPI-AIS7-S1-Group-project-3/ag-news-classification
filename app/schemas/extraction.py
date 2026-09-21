from enum import Enum
from pydantic import BaseModel, Field

class SentimentEnum(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"

class NewsExtraction(BaseModel):
    """
    Schema for extracting structured information from a news article.
    """
    topic_keywords: list[str] = Field(
        default_factory=list, 
        description="A list of 3-5 key phrases or topics discussed in the news article, lowercase."
    )
    entities: list[str] = Field(
        default_factory=list,
        description="A list of prominent named entities (people, organizations, locations) mentioned in the text."
    )
    summary: str = Field(
        default="", 
        description="A concise, 1-2 sentence summary of the main point of the article."
    )
    sentiment: SentimentEnum = Field(
        default=SentimentEnum.NEUTRAL,
        description="The overall sentiment of the news text."
    )
    is_breaking_news: bool = Field(
        default=False,
        description="True if the text appears to report breaking, urgent, or rapidly developing news."
    )
