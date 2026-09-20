import logging
import time

from app.pipeline.fallback import keyword_fallback, safe_classify

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Normalize raw text before it enters the LLM or fallback path."""
    if text is None:
        return ""
    return " ".join(str(text).split())


def run_pipeline(text: str) -> dict:
    """Classify one news text. Always returns a dict; never raises for model/network problems."""
    start = time.perf_counter()
    cleaned = clean_text(text)

    if not cleaned:
        # Nothing to classify: don't waste a Groq call on it.
        result, used_fallback = keyword_fallback(""), True
    else:
        result, used_fallback = safe_classify(cleaned)

    elapsed = round(time.perf_counter() - start, 3)
    logger.info("pipeline done | category=%s | fallback=%s | %.3fs",
                result.category.value, used_fallback, elapsed)
    return {
        "category": result.category.value,
        "confidence": result.confidence,
        "used_fallback": used_fallback,
        "elapsed_seconds": elapsed,
    }


def run_pipeline_batch(texts: list[str], batch_size: int = 5, delay_seconds: float = 0.5) -> list[dict]:
    """Process a list of texts in chunks to reduce Groq burst rate-limit pressure."""
    results: list[dict] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        for text in batch:
            results.append(run_pipeline(text))
        if delay_seconds > 0 and i + batch_size < len(texts):
            time.sleep(delay_seconds)
    return results