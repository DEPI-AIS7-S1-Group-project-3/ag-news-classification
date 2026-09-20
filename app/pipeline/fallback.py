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
                            "technology", "chip", "microsoft", "google", "apple", "online", "nasa",
                            "ai", "startup", "launch", "battery", "semiconductor", "cybersecurity"},
    NewsCategory.WORLD: {"president", "government", "minister", "war", "iraq", "election",
                         "police", "military", "un", "troops", "talks", "attack", "policy"},
}


def keyword_scores(text: str) -> dict[NewsCategory, int]:
    words = set(re.findall(r"[a-z]+", text.lower()))
    return {cat: len(words & kws) for cat, kws in KEYWORDS.items()}


def keyword_fallback(text: str) -> NewsClassification:
    scores = keyword_scores(text)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return NewsClassification(category=NewsCategory.WORLD, confidence=0.0,
                                  reasoning="fallback: no keyword matched")
    return NewsClassification(category=best, confidence=0.3,
                              reasoning=f"fallback: {scores[best]} keyword match(es)")


def _guard_against_common_mistakes(text: str, result: NewsCategory) -> NewsCategory:
    scores = keyword_scores(text)

    if result == NewsCategory.BUSINESS:
        if scores[NewsCategory.SCI_TECH] >= scores[NewsCategory.BUSINESS] + 2 and scores[NewsCategory.SCI_TECH] >= 2:
            return NewsCategory.SCI_TECH
        if scores[NewsCategory.WORLD] >= scores[NewsCategory.BUSINESS] + 2 and scores[NewsCategory.WORLD] >= 2:
            return NewsCategory.WORLD

    if result == NewsCategory.SCI_TECH:
        if scores[NewsCategory.BUSINESS] >= scores[NewsCategory.SCI_TECH] + 2 and scores[NewsCategory.BUSINESS] >= 2:
            return NewsCategory.BUSINESS

    if result == NewsCategory.WORLD:
        if scores[NewsCategory.BUSINESS] >= scores[NewsCategory.WORLD] + 2 and scores[NewsCategory.BUSINESS] >= 2:
            return NewsCategory.BUSINESS
        if scores[NewsCategory.SPORTS] >= scores[NewsCategory.WORLD] + 2 and scores[NewsCategory.SPORTS] >= 2:
            return NewsCategory.SPORTS

    return result


def safe_classify(text: str) -> tuple[NewsClassification, bool]:
    """Returns (result, used_fallback). Never raises PipelineError."""
    try:
        predicted = classify_with_retry(text)
        corrected_category = _guard_against_common_mistakes(text, predicted.category)
        if corrected_category != predicted.category:
            corrected = NewsClassification(
                category=corrected_category,
                confidence=0.8,
                reasoning="guardrail: keyword override"
            )
            return corrected, True
        return predicted, False
    except PipelineError as e:
        logger.warning("fallback triggered after retries: %s", e)
        return keyword_fallback(text), True


def safe_pipeline(text: str) -> tuple[NewsClassification, bool]:
    """Notebook-style compatibility wrapper matching the app's no-crash contract."""
    return safe_classify(text)