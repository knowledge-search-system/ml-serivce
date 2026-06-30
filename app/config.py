from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ML_SERVICE_", env_file=".env", extra="ignore")

    http_port: int = 8083
    postgres_dsn: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/ml_service"
    openai_api_key: str = ""
    openai_base_url: str | None = None
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    embedding_batch_size: int = 64
    llm_model: str = "gpt-4.1-nano"
    top_k: int = 5
    min_score: float = 0.35
    chunk_size_tokens: int = 800
    chunk_overlap_tokens: int = 150
    max_file_size_bytes: int = 10485760
    log_level: str = "info"
