class PipelineError(Exception):
    """Raised when one attempt to classify a text fails (Groq error, bad JSON, invalid category...).

    Every failure inside classify.py is converted to this single type, so retry.py and
    fallback.py only ever need to watch for ONE exception.
    """