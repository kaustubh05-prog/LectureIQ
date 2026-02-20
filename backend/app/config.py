from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_secret_key: str
    app_debug: bool = False

    # Database
    database_url: str

    # Redis / Celery
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str

    # AWS S3
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "ap-south-1"
    s3_bucket_name: str

    # AI Services
    groq_api_key: str
    youtube_api_key: str

    # Whisper
    whisper_model: str = "base"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
