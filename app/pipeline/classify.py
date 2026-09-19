import json

from pydantic import ValidationError

from app.core.config import settings
from app.pipeline.errors import PipelineError
from app.pipeline.groq_client import call_groq
from app.schemas.classification import NewsCategory, NewsClassification

CATEGORIES = [c.value for c in NewsCategory]

# Two short examples for the two categories models mix up the most.
FEW_SHOTS = (
    "Examples:\n\n"
    'Article: "Shares of the chipmaker jumped 8% after it raised its full-year revenue forecast."\n'
    '{"category": "Business", "confidence": 0.9, "reasoning": "Stock move and earnings forecast"}\n\n'
    'Article: "Researchers unveil a battery that charges a phone in five minutes."\n'
    '{"category": "Sci/Tech", "confidence": 0.9, "reasoning": "New technology research result"}\n\n'
    'Article: "The chipmaker unveiled its new AI processor, sending shares up 12% in early trading."\n'
    '{"category": "Sci/Tech", "confidence": 0.85, "reasoning": "Main subject is the new chip, stock move is secondary"}\n\n'
)


def build_classification_prompt(text: str) -> str:
    return (
        f"Classify this news article into exactly one of these categories: {CATEGORIES}.\n"
        'Respond as JSON: {"category": "<one of the categories>", '
        '"confidence": <float 0-1>, "reasoning": "<max 15 words>"}.\n\n'
        f"{FEW_SHOTS}"
        f'Article:\n"""\n{text[:settings.MAX_INPUT_CHARS]}\n"""'
    )


def classify_news(text: str) -> NewsClassification:
    """One attempt: prompt -> Groq -> parse JSON -> validate. Any failure becomes PipelineError."""
    prompt = build_classification_prompt(text)
    try:
        raw = call_groq(prompt)
        payload = json.loads(raw)
        return NewsClassification(**payload)
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        # The model answered, but the answer is unusable (bad JSON / unknown category / confidence 1.5)
        raise PipelineError(f"invalid model reply: {e}") from e
    except Exception as e:
        # Groq itself failed (rate limit, timeout, no network, missing key...)
        raise PipelineError(f"groq call failed: {e!r}") from e