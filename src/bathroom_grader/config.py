from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, loaded from environment variables (or a .env file)."""

    database_url: str = "postgresql+psycopg://localhost/bathroom_grader"

    # e.g. LOG_LEVEL=DEBUG uvicorn bathroom_grader.main:app --reload
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
