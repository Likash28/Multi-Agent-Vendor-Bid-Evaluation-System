"""
Application Configuration
Uses Pydantic Settings for environment variable management
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars not defined in model
    )

    # Application
    APP_NAME: str = "GovProcure"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-in-production"

    # Database (SQLite)
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/govprocure.db"

    # File Storage (local)
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB in bytes
    ALLOWED_FILE_TYPES: str = "pdf,docx,doc,xlsx,xls"

    # JWT Authentication
    JWT_SECRET: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI/LLM (AWS Bedrock)
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    BEDROCK_MODEL_ID: str = "anthropic.claude-sonnet-4-20250514-v1:0"
    LLM_TEMPERATURE: float = 0.2
    LLM_TIMEOUT: int = 120

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    # Application URL
    FRONTEND_URL: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS into a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Parse ALLOWED_FILE_TYPES into a list"""
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
