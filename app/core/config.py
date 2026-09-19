from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AG News Text Classification Pipeline"
    API_V1_STR: str = "/api/v1"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TIMEOUT_SECONDS: float = 20.0
    MAX_INPUT_CHARS: int = 2000
    RETRY_ATTEMPTS: int = 3

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()