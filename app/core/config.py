from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AG News Text Classification Pipeline"
    API_V1_STR: str = "/api/v1"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GROQ_TIMEOUT_SECONDS: float = 20.0
    MAX_INPUT_CHARS: int = 2000
    RETRY_ATTEMPTS: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()