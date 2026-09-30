from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, read from environment variables (and `.env` locally)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ANTHROPIC_API_KEY is read by the Anthropic SDK directly; it is not duplicated here.
    llm_model: str = "claude-opus-5-5"
    llm_max_tokens: int = 16000
    llm_effort: Literal["low", "medium", "high", "xhigh", "max"] = "medium"

    # Shared secret clients must send as `X-API-Key`. Empty = auth disabled (local dev only).
    app_api_key: SecretStr = SecretStr("")


@lru_cache
def get_settings() -> Settings:
    return Settings()
