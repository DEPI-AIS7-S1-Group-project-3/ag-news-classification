import json
from pydantic import ValidationError

from app.core.config import settings
from app.pipeline.errors import PipelineError
from app.pipeline.llm_client import call_llm
from app.schemas.extraction import NewsExtraction

def build_extraction_prompt(text: str) -> str:
    return (
        "Extract the following structured information from the provided news article:\n\n"
        "1. topic_keywords: A list of 3-5 key phrases or topics discussed in the news article, lowercase.\n"
        "2. entities: A list of prominent named entities (people, organizations, locations) mentioned in the text.\n"
        "3. summary: A concise, 1-2 sentence summary of the main point of the article.\n"
        "4. sentiment: The overall sentiment of the news text. Must be exactly 'Positive', 'Negative', or 'Neutral'.\n"
        "5. is_breaking_news: Boolean indicating if it appears to report breaking, urgent, or rapidly developing news (true/false).\n\n"
        "Respond as valid JSON only, matching this schema:\n"
        '{"topic_keywords": ["keyword1", "keyword2"], "entities": ["Entity1", "Entity2"], "summary": "...", "sentiment": "Neutral", "is_breaking_news": false}\n\n'
        'Article:\n"""\n'
        f"{text[:settings.MAX_INPUT_CHARS]}\n"
        '"""'
    )

def validate_extraction(payload: dict) -> NewsExtraction:
    """Validate and normalize a parsed Groq response into the app extraction schema."""
    if not isinstance(payload, dict):
        raise TypeError(f"expected a dict payload, got {type(payload).__name__}")
    return NewsExtraction(**payload)

def extract_news(text: str) -> NewsExtraction:
    """One attempt: prompt -> Groq -> parse JSON -> validate. Any failure becomes PipelineError."""
    prompt = build_extraction_prompt(text)
    try:
        raw = call_llm(prompt)
        payload = json.loads(raw)
        return validate_extraction(payload)
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        raise PipelineError(f"invalid model reply for extraction: {e}") from e
    except Exception as e:
        raise PipelineError(f"llm call failed for extraction: {e!r}") from e
