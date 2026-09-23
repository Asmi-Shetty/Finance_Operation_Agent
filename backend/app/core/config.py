from functools import lru_cache
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI Finance Operations Agent"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite+aiosqlite:///./finance_agent.db"
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: Path = Path("uploads")
    max_upload_bytes: int = 10 * 1024 * 1024
    extraction_confidence_threshold: float = 0.85
    po_variance_tolerance: float = 0.05
    llm_provider: str = "openai"
    llm_model: str = ""
    openai_api_key: str = ""
    langfuse_enabled: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        return value.split(",") if isinstance(value, str) else value

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

