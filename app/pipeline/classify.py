import json

from pydantic import ValidationError

from app.core.config import settings
from app.pipeline.errors import PipelineError
from app.pipeline.llm_client import call_llm
from app.schemas.classification import NewsCategory, NewsClassification


def validate_classification(payload: dict) -> NewsClassification:
    """Validate and normalize a parsed Groq response into the app schema."""
    if not isinstance(payload, dict):
        raise TypeError(f"expected a dict payload, got {type(payload).__name__}")
    return NewsClassification(**payload)

CATEGORIES = [c.value for c in NewsCategory]

# Minimized few-shot examples to save Tokens Per Minute
FEW_SHOTS = (
    "Examples:\n\n"
    'Article: "Shares of the chipmaker jumped 8% after it raised its full-year revenue forecast."\n'
    '{"category": "Business", "confidence": 0.95, "reasoning": "Stock move and earnings forecast"}\n\n'
    'Article: "The United Nations Security Council convened today to vote on the new peace resolution."\n'
    '{"category": "World", "confidence": 0.98, "reasoning": "International government/diplomacy"}\n\n'
)


def build_classification_prompt(text: str) -> str:
    return (
        "You are an expert news desk editor. Classify this news snippet into EXACTLY ONE of these categories: "
        f"{CATEGORIES}.\n\n"
        "Strict Classification Guidelines:\n"
        "- Business: Use for ANY mention of stocks, earnings, corporate mergers, oil/gas prices, banks, or broad economy.\n"
        "- World: Use for international politics, elections, government actions, diplomacy, police/military, and foreign affairs.\n"
        "- Sports: Use for athletic events, game scores, team news, Olympics, and player transfers.\n"
        "- Sci/Tech: Use for scientific discoveries, space exploration, new software/hardware, internet, and AI.\n\n"
        "Ambiguity Rules:\n"
        "1. If an article is about a tech company (like Microsoft) but focuses on their stock price or a lawsuit, it is 'Business'.\n"
        "2. If an article is about a political figure but heavily focuses on the stock market impact, tip towards 'Business'.\n"
        "3. Focus on the core 'event' of the text, not just the names mentioned.\n\n"
        f"{FEW_SHOTS}\n\n"
        "Now, perform the classification for the following article. Respond with a single valid JSON object containing exactly the three fields: 'category', 'confidence', and 'reasoning'. Do NOT provide any additional text or examples.\n"
        "Respond as valid JSON only, using exactly this format: "
        '{"category": "category_name", "confidence": 0.99, "reasoning": "rationale"}\n\n'
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
        raw = call_llm(prompt)
        # Strip markdown fences in case the Groq model returns ```json ... ```
        if raw.startswith("```"):
            raw = raw.strip("`").strip().removeprefix("json").strip()
            
        payload = json.loads(raw)
        return validate_classification(payload)
    except (json.JSONDecodeError, ValidationError) as e:
        # If the generated string was cut off but has a category, try regex
        import re
        match = re.search(r'"category"\s*:\s*"([^"]+)"', raw)
        if match and match.group(1) in CATEGORIES:
            return NewsClassification(
                category=match.group(1),
                confidence=0.5,
                reasoning=f"Regex fallback due to JSON error"
            )
        raise PipelineError(f"invalid model reply: {e}") from e
    except Exception as e:
        # LLM itself failed (rate limit, timeout, no network, missing key...)
        raise PipelineError(f"llm call failed: {e!r}") from e