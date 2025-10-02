"""Configuration management for BankEaseAI API."""

from pydantic import BaseModel
from typing import Optional
from functools import lru_cache
import os


class Settings(BaseModel):
    """Application settings.

    Loads configuration from environment variables.
    """

    # Application
    APP_NAME: str = "BankEaseAI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Database
    DATABASE_URL: str = "sqlite:///./bankeaseai.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "https://localhost:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".pdf"}
    UPLOAD_DIR: str = "./uploads"
    OUTPUT_DIR: str = "./output"

    # AI Providers
    AI_PROVIDER: str = "openai"  # openai, anthropic, google
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # AI Model Settings
    DEFAULT_MODEL: str = "gpt-4o"
    AI_TEMPERATURE: float = 0.1
    AI_MAX_TOKENS: int = 4000
    AI_TIMEOUT: int = 120  # seconds

    # Usage Limits (per user)
    FREE_TIER_MONTHLY_LIMIT: int = 10
    BASIC_TIER_MONTHLY_LIMIT: int = 100
    PRO_TIER_MONTHLY_LIMIT: int = 1000

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 hour

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = False

    def get_database_url(self) -> str:
        """Get database URL with environment-specific adjustments.

        Returns:
            Database connection URL
        """
        if self.ENVIRONMENT == "production":
            # In production, use PostgreSQL
            return self.DATABASE_URL
        elif self.ENVIRONMENT == "test":
            # In test, use in-memory SQLite
            return "sqlite:///:memory:"
        else:
            # In development, use file-based SQLite
            return self.DATABASE_URL

    def get_ai_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """Get API key for specified AI provider.

        Args:
            provider: Provider name (defaults to configured provider)

        Returns:
            API key string or None
        """
        provider = provider or self.AI_PROVIDER

        if provider == "openai":
            return self.OPENAI_API_KEY
        elif provider == "anthropic":
            return self.ANTHROPIC_API_KEY
        elif provider == "google":
            return self.GOOGLE_API_KEY
        else:
            return None

    def ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    def is_production(self) -> bool:
        """Check if running in production.

        Returns:
            True if production environment
        """
        return self.ENVIRONMENT == "production"

    def get_usage_limit(self, tier: str) -> int:
        """Get usage limit for user tier.

        Args:
            tier: User tier (free, basic, pro)

        Returns:
            Monthly usage limit
        """
        tier_limits = {
            "free": self.FREE_TIER_MONTHLY_LIMIT,
            "basic": self.BASIC_TIER_MONTHLY_LIMIT,
            "pro": self.PRO_TIER_MONTHLY_LIMIT
        }
        return tier_limits.get(tier.lower(), self.FREE_TIER_MONTHLY_LIMIT)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings singleton instance
    """
    settings = Settings()
    settings.ensure_directories()
    return settings


# Convenience exports
settings = get_settings()
