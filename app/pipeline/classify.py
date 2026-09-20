import json

from pydantic import ValidationError

from app.core.config import settings
from app.pipeline.errors import PipelineError
from app.pipeline.groq_client import call_groq
from app.schemas.classification import NewsCategory, NewsClassification


def validate_classification(payload: dict) -> NewsClassification:
    """Validate and normalize a parsed Groq response into the app schema."""
    if not isinstance(payload, dict):
        raise TypeError(f"expected a dict payload, got {type(payload).__name__}")
    return NewsClassification(**payload)

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
        "Classify this news article into exactly one of these categories: "
        f"{CATEGORIES}.\n\n"
        "Use these strict rules:\n"
        "- Business: earnings, stocks, markets, mergers, bank/finance, inflation, revenue, corporate performance.\n"
        "- World: politics, government, diplomacy, war, conflict, sanctions, elections, public policy.\n"
        "- Sports: games, teams, scores, leagues, players, tournaments, transfers, championships.\n"
        "- Sci/Tech: AI, software, chips, cybersecurity, biotech, research, space, internet, startups, product launches.\n"
        "If the article is mainly about stock prices or company finances, choose Business. "
        "If the article is mainly about a product, research breakthrough, AI, chips, software, or tech launch, choose Sci/Tech.\n"
        "Never choose a category just because the headline mentions money or a tech company; use the main subject of the story.\n\n"
        "Respond as valid JSON only, with this exact shape: "
        '{"category": "<one of the categories>", "confidence": <float 0-1>, "reasoning": "<max 15 words>"}.\n\n'
        f"{FEW_SHOTS}"
        'Article:\n"""\n'
        f"{text[:settings.MAX_INPUT_CHARS]}\n"
        '"""'
    )


def validate_classification(payload: dict) -> NewsClassification:
    """Validate and normalize a parsed Groq response into the app schema."""
    if not isinstance(payload, dict):
        raise TypeError(f"expected a dict payload, got {type(payload).__name__}")
    return NewsClassification(**payload)


def classify_news(text: str) -> NewsClassification:
    """One attempt: prompt -> Groq -> parse JSON -> validate. Any failure becomes PipelineError."""
    prompt = build_classification_prompt(text)
    try:
        raw = call_groq(prompt)
        payload = json.loads(raw)
        return validate_classification(payload)
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        # The model answered, but the answer is unusable (bad JSON / unknown category / confidence 1.5)
        raise PipelineError(f"invalid model reply: {e}") from e
    except Exception as e:
        # Groq itself failed (rate limit, timeout, no network, missing key...)
        raise PipelineError(f"groq call failed: {e!r}") from e