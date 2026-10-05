from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, loaded from environment variables (or a .env file)."""

    database_url: str = "postgresql+psycopg://localhost/bathroom_grader"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
