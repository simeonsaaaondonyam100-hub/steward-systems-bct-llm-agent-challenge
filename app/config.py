from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="STEWARD_")

    app_name: str = "Steward Systems BCT LLM Agent Challenge"
    service_name: str = "steward-bct-agent"
    app_version: str = "0.1.0"
    data_dir: Path = Field(default=BASE_DIR / "data" / "sample")
    use_llm: bool = False
    openai_api_key: str | None = None

    semantic_weight: float = 0.30
    preference_weight: float = 0.25
    context_weight: float = 0.20
    quality_weight: float = 0.15
    nigerian_context_weight: float = 0.10


@lru_cache
def get_settings() -> Settings:
    return Settings()
