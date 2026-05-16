"""Configuration settings for RepoTwin backend."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "RepoTwin"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    
    # Database
    database_url: PostgresDsn = PostgresDsn("postgresql+asyncpg://user:password@localhost:5432/repotwin")
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Redis
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")
    redis_pool_size: int = 20
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"
    
    # IBM watsonx.ai
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_model_id: str = "ibm-granite-13b-chat-v2"
    watsonx_max_tokens: int = 4096
    watsonx_temperature: float = 0.1
    watsonx_top_p: float = 0.9
    watsonx_rate_limit_per_minute: int = 100
    
    # Git
    git_clone_timeout: int = 300
    git_max_repo_size_mb: int = 500
    git_storage_path: str = "/tmp/repotwin/repos"
    
    # Analysis
    analysis_max_context_size: int = 100000  # characters
    analysis_timeout_seconds: int = 300
    max_files_per_analysis: int = 50
    
    # Caching
    cache_ttl_repository: int = 3600  # 1 hour
    cache_ttl_dependency_graph: int = 3600  # 1 hour
    cache_ttl_analysis_results: int = 86400  # 24 hours
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Frontend URL for CORS
    frontend_url: str = "http://localhost:3000"
    allowed_origins_str: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 100
    
    @property
    def allowed_origins(self) -> List[str]:
        """Parse comma-separated origins from string."""
        if not self.allowed_origins_str or self.allowed_origins_str.strip() == "":
            return ["http://localhost:3000"]
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]
    
    @property
    def async_database_url(self) -> str:
        """Get async database URL."""
        url = str(self.database_url)
        if "postgresql://" in url:
            return url.replace("postgresql://", "postgresql+asyncpg://")
        if "postgres://" in url:
            return url.replace("postgres://", "postgresql+asyncpg://")
        return url
    
    @property
    def sync_database_url(self) -> str:
        """Get sync database URL for migrations."""
        url = str(self.database_url)
        if "postgresql+asyncpg://" in url:
            return url.replace("postgresql+asyncpg://", "postgresql://")
        if "postgres://" in url:
            return url.replace("postgres://", "postgresql://")
        return url


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
