import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sanskrit IR Enhancement Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sanskrit_ir_secret_key_super_secure_2026_dev")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sanskrit_ir.db")
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "")

    class Config:
        case_sensitive = True

settings = Settings()
