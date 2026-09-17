from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AG News Text Classification Pipeline"
    API_V1_STR: str = "/api/v1"
    GROQ_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()