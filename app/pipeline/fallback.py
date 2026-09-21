import json
import logging

from pydantic import ValidationError

from app.pipeline.errors import PipelineError
from app.pipeline.retry import classify_with_retry
from app.pipeline.openai_client import call_openai
from app.pipeline.classify import build_classification_prompt
from app.schemas.classification import NewsClassification

logger = logging.getLogger(__name__)


def classify_with_openai(text: str) -> NewsClassification:
    """
    Fallback classification using OpenAI.

    This function performs one OpenAI attempt.
    Retry logic is handled separately.
    """

    prompt = build_classification_prompt(text)

    try:
        raw = call_openai(prompt)

        # Remove markdown code fences if the model returns them.
        if raw.startswith("```"):
            raw = raw.strip("`").strip()

            if raw.startswith("json"):
                raw = raw.removeprefix("json").strip()

        payload = json.loads(raw)

        if not isinstance(payload, dict):
            raise TypeError(
                f"expected a dict payload, got {type(payload).__name__}"
            )

        return NewsClassification(**payload)

    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        raise PipelineError(
            f"invalid OpenAI fallback response: {e}"
        ) from e

    except Exception as e:
        raise PipelineError(
            f"OpenAI fallback call failed: {e!r}"
        ) from e


def safe_classify(text: str) -> tuple[NewsClassification, bool]:
    """
    Primary → fallback classification strategy.

    1. Try Groq with the existing retry mechanism.
    2. If Groq completely fails, try OpenAI.
    3. If OpenAI also fails, raise PipelineError.

    Returns:
        (classification_result, used_fallback)
    """

    # --------------------------------------------------
    # 1. PRIMARY PROVIDER: GROQ
    # --------------------------------------------------
    try:
        result = classify_with_retry(text)

        logger.info(
            "classification succeeded using Groq | category=%s",
            result.category.value,
        )

        return result, False

    except PipelineError as groq_error:
        logger.warning(
            "Groq failed after retries. Switching to OpenAI fallback: %s",
            groq_error,
        )

    # --------------------------------------------------
    # 2. FALLBACK PROVIDER: OPENAI
    # --------------------------------------------------
    try:
        result = classify_with_openai(text)

        logger.info(
            "classification succeeded using OpenAI fallback | category=%s",
            result.category.value,
        )

        return result, True

    except PipelineError as openai_error:
        logger.error(
            "Both Groq and OpenAI failed. Groq fallback chain exhausted: %s",
            openai_error,
        )

        raise PipelineError(
            "Classification failed: both Groq and OpenAI providers failed."
        ) from openai_error


def safe_pipeline(
    text: str,
) -> tuple[NewsClassification, bool]:
    """
    Compatibility wrapper used by the application.
    """

    return safe_classify(text)