"""Runtime configuration for the HALORA backend."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    """Small dependency-free settings object backed by environment variables."""

    app_name: str = os.getenv("HALORA_APP_NAME", "HALORA")
    app_version: str = os.getenv("HALORA_APP_VERSION", "1.0.0")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    cors_origins: list[str] = _csv_env(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
