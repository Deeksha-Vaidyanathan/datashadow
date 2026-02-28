from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/datashadow"
    hibp_api_key: str | None = None
    openai_api_key: str | None = None
    user_agent: str = "DataShadow-Personal-Data-Auditor/1.0"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
