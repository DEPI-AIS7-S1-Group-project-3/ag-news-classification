import logging
import time

from app.pipeline.fallback import keyword_fallback, safe_classify

logger = logging.getLogger(__name__)


def run_pipeline(text: str) -> dict:
    """Classify one news text. Always returns a dict; never raises for model/network problems."""
    start = time.perf_counter()

    if not text or not text.strip():
        # Nothing to classify: don't waste a Groq call on it.
        result, used_fallback = keyword_fallback(""), True
    else:
        result, used_fallback = safe_classify(text.strip())

    elapsed = round(time.perf_counter() - start, 3)
    logger.info("pipeline done | category=%s | fallback=%s | %.3fs",
                result.category.value, used_fallback, elapsed)
    return {
        "category": result.category.value,
        "confidence": result.confidence,
        "used_fallback": used_fallback,
        "elapsed_seconds": elapsed,
    }