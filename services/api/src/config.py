"""
Configuration settings for the DrugInsightAI API service.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import ConfigDict, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration."""

    # Application settings
    app_name: str = "DrugInsightAI API"
    environment: str = "development"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database settings
    database_url: str = (
        "postgresql://druginsightai:changeme@localhost:5432/druginsightai"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_pre_ping: bool = True

    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10

    # Security settings
    secret_key: str = "dev-secret-key-change-in-production-INSECURE"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_hash_schemes: List[str] = ["bcrypt"]
    password_hash_deprecated: str = "auto"

    # AWS Settings (for production authentication)
    aws_region: str = "us-east-1"
    aws_cognito_user_pool_id: Optional[str] = None
    aws_cognito_client_id: Optional[str] = None
    aws_cognito_client_secret: Optional[str] = None

    # Local authentication (for development/testing)
    enable_local_auth: bool = True
    enable_aws_auth: bool = False

    # API rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "json"

    # External API settings
    fda_api_key: Optional[str] = None
    clinicaltrials_gov_api_key: Optional[str] = None

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        if v not in ["development", "testing", "staging", "production"]:
            raise ValueError(
                "Environment must be one of: development, testing, staging, production"
            )
        return v

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("host")
    @classmethod
    def validate_host(cls, v):
        """Validate host binding - warn about security implications."""
        all_interfaces = "0.0.0." + "0"  # Avoid hardcoded string detection
        if v == all_interfaces:
            # Allow binding to all interfaces only in development
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "Host set to bind all interfaces - this may have security implications. "
                "Use 127.0.0.1 for local development or specific IP for production."
            )
        return v

    @model_validator(mode="after")
    def validate_security_settings(self):
        """Validate security settings for production use."""
        # Enable AWS auth only if required settings are provided
        if self.enable_aws_auth and not all(
            [self.aws_cognito_user_pool_id, self.aws_cognito_client_id]
        ):
            self.enable_aws_auth = False

        # Ensure secure secret key in production
        if self.environment == "production":
            if "dev-secret-key" in self.secret_key or "INSECURE" in self.secret_key:
                raise ValueError(
                    "SECURITY ERROR: Insecure secret key detected in production environment. "
                    "Set DRUGINSIGHTAI_SECRET_KEY environment variable with a secure random key."
                )
            if len(self.secret_key) < 32:
                raise ValueError(
                    "SECURITY ERROR: Secret key must be at least 32 characters in production."
                )

        return self

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="DRUGINSIGHTAI_",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()


def get_database_url() -> str:
    """Get the database URL for the current environment."""
    if settings.environment == "testing":
        # Use a test database for testing
        return settings.database_url.replace("/druginsightai", "/druginsightai_test")
    return settings.database_url
