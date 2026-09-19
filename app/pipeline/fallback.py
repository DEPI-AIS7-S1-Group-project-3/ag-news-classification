import logging
import re

from app.pipeline.errors import PipelineError
from app.pipeline.retry import classify_with_retry
from app.schemas.classification import NewsCategory, NewsClassification

logger = logging.getLogger(__name__)

# A tiny keyword scorer used ONLY when Groq keeps failing. It needs no model, no internet
# and no extra libraries, so it can't fail the same way Groq did.
KEYWORDS = {
    NewsCategory.SPORTS: {"game", "team", "season", "coach", "league", "cup", "match", "player",
                          "win", "won", "score", "champion", "tournament", "olympic"},
    NewsCategory.BUSINESS: {"stock", "shares", "market", "profit", "company", "bank", "economy",
                            "oil", "price", "sales", "earnings", "investor", "billion", "revenue"},
    NewsCategory.SCI_TECH: {"software", "internet", "computer", "research", "scientist", "space",
                            "technology", "chip", "microsoft", "google", "apple", "online", "nasa"},
    NewsCategory.WORLD: {"president", "government", "minister", "war", "iraq", "election",
                         "police", "military", "un", "troops", "talks", "attack"},
}


def keyword_fallback(text: str) -> NewsClassification:
    words = set(re.findall(r"[a-z]+", text.lower()))
    scores = {cat: len(words & kws) for cat, kws in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        # Nothing matched: we truly don't know. World is just a placeholder, confidence 0.0 says so.
        return NewsClassification(category=NewsCategory.WORLD, confidence=0.0,
                                  reasoning="fallback: no keyword matched")
    return NewsClassification(category=best, confidence=0.3,
                              reasoning=f"fallback: {scores[best]} keyword match(es)")


def safe_classify(text: str) -> tuple[NewsClassification, bool]:
    """Returns (result, used_fallback). Never raises PipelineError."""
    try:
        return classify_with_retry(text), False
    except PipelineError as e:
        logger.warning("fallback triggered after retries: %s", e)
        return keyword_fallback(text), True