from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Supply Chain Optimization Agent"
    app_version: str = "0.1.0"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/supply_chain"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/supply_chain"

    openai_api_key: str = ""
    openweather_api_key: str = ""

    prophet_forecast_horizon_days: int = 30
    default_safety_stock_days: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
