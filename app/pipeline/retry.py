import logging

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.pipeline.classify import classify_news
from app.pipeline.errors import PipelineError
from app.schemas.classification import NewsClassification

logger = logging.getLogger(__name__)


def _log_retry(retry_state):
    # tenacity calls this right before it waits and tries again.
    logger.warning(
        "retry | attempt %d failed: %s | waiting %.1fs",
        retry_state.attempt_number, retry_state.outcome.exception(), retry_state.next_action.sleep,
    )


@retry(
    stop=stop_after_attempt(settings.RETRY_ATTEMPTS),         # e.g. 3 tries in total
    wait=wait_exponential(multiplier=1, min=1, max=8),        # wait ~1s, then ~2s, then ~4s (max 8s)
    retry=retry_if_exception_type(PipelineError),             # only retry OUR error type
    reraise=True,                                             # after the last try, raise the real error
    before_sleep=_log_retry,
)
def classify_with_retry(text: str) -> NewsClassification:
    return classify_news(text)