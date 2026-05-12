from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://neuralmap:neuralmap@localhost:5432/neuralmap"

    google_client_id: str = ""
    google_client_secret: str = ""

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    frontend_url: str = "http://localhost:3000"

    weights_dir: str = "weights"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
