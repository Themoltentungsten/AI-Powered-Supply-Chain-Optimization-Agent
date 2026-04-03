# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: Initial configuration class (app name, DB URL, OpenAI key)
#  DAY 2: Added weather provider settings, switched default to SQLite
#  DAY 4: Added agent model settings
# ═══════════════════════════════════════════════════════════════════════

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_REPO_ROOT / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── DAY 1 START: Core application settings ───────────────────────
    app_name: str = "Supply Chain Optimization Agent"
    app_version: str = "0.1.0"
    debug: bool = True

    database_url: str = "sqlite:///./supply_chain.db"

    openai_api_key: str = ""

    prophet_forecast_horizon_days: int = 30
    default_safety_stock_days: int = 7
    # ── DAY 1 END ────────────────────────────────────────────────────

    # ── DAY 2 START: Weather API configuration ───────────────────────
    weather_provider: str = "weatherapi"
    weatherapi_key: str = ""
    # ── DAY 2 END ────────────────────────────────────────────────────

    # ── DAY 4 START: Agent / LLM settings ─────────────────────────────
    agent_llm_model: str = "gpt-4o-mini"
    agent_temperature: float = 0.3
    # ── DAY 4 END ────────────────────────────────────────────────────


@lru_cache
def get_settings() -> Settings:
    return Settings()
