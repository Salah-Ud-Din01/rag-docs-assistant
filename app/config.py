from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Values can be overridden with environment variables or a .env file,
    e.g. APP_VERSION=0.2.0
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "RAG Docs Assistant"
    app_version: str = "0.1.0"


settings = Settings()