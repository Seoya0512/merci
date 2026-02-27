import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

_env = os.getenv("APP_ENV", "dev")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f".env.{_env}")

    APP_ENV: str = "dev"

    # DB
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # OAuth - Kakao
    KAKAO_CLIENT_ID: str = ""
    KAKAO_REDIRECT_URI: str = ""

    # OAuth - Naver
    NAVER_CLIENT_ID: str = ""
    NAVER_CLIENT_SECRET: str = ""
    NAVER_REDIRECT_URI: str = ""

    # Cloudflare R2 (S3 호환)
    CF_ACCOUNT_ID: str = ""
    CF_R2_ACCESS_KEY_ID: str = ""
    CF_R2_SECRET_ACCESS_KEY: str = ""
    CF_R2_BUCKET_NAME: str = ""
    CF_R2_PUBLIC_URL: str = ""

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Swagger
    SHOW_DOCS: bool = True


settings = Settings()
