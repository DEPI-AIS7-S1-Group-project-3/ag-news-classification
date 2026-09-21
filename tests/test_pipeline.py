import pytest

from app.pipeline.classify import classify_news, validate_classification
from app.pipeline.errors import PipelineError
from app.schemas.classification import NewsCategory, NewsClassification


def test_validate_classification_accepts_valid_payload():
    model = validate_classification({
        "category": "Business",
        "confidence": 0.82,
        "reasoning": "Strong earnings outlook and price action",
    })

    assert isinstance(model, NewsClassification)
    assert model.category is NewsCategory.BUSINESS
    assert model.confidence == 0.82


def test_classify_news_wraps_invalid_model_output_as_pipeline_error(monkeypatch):
    monkeypatch.setattr(
        "app.pipeline.classify.call_llm",
        lambda _prompt: '{"category": "Unknown", "confidence": 1.5, "reasoning": "bad"}',
    )

    with pytest.raises(PipelineError, match="invalid model reply"):
        classify_news("Apple unveils a new chip.")
