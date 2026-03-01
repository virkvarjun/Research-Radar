from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://research_radar:research_radar_dev@localhost:5432/research_radar"
    database_url_sync: str = "postgresql://research_radar:research_radar_dev@localhost:5432/research_radar"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth - Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = "super-secret-jwt-token-for-dev"

    # Embeddings
    embedding_provider: str = "openai"  # "openai" | "sentence-transformers"
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    # Email
    resend_api_key: str = ""
    email_from: str = "Research Radar <digest@researchradar.dev>"

    # External APIs
    openalex_email: str = "dev@researchradar.dev"

    # App
    app_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    feedback_secret: str = "feedback-signing-secret-change-me"

    # Ranking
    alpha_like: float = 0.1
    beta_dislike: float = 0.05
    mmr_lambda: float = 0.7
    feed_size: int = 20
    digest_size: int = 5
    novelty_days: int = 7

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
