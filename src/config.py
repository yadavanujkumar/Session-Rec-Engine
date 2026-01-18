"""Configuration management for the session-based recommendation system."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "protected_namespaces": (),
    }

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    session_expiry_seconds: int = 1800  # 30 minutes

    # Qdrant Configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "items"

    # Model Configuration
    model_name: str = "sasrec"
    sequence_length: int = 5
    embedding_dim: int = 128
    num_heads: int = 4
    num_layers: int = 2
    dropout: float = 0.1

    # Recommendation Configuration
    top_k: int = 5
    cold_start_threshold: int = 2

    # Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
