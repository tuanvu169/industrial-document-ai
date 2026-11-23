from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    app_name: str = "Industrial Document AI"
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""  # backend only, never ship to frontend
    storage_bucket: str = "documents"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    gemini_timeout_s: int = 60
    gemini_max_retries: int = 2

    # Embeddings / chunking / retrieval
    embedding_model: str = "intfloat/multilingual-e5-small"
    embedding_dim: int = 384
    chunk_size_tokens: int = 500
    chunk_overlap_tokens: int = 80
    retrieval_top_k: int = 6
    retrieval_candidates: int = 20
    rrf_k: int = 60
    history_messages: int = 6

    # Upload limits
    max_upload_mb: int = 20
    max_pages: int = 500

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
