"""Runtime configuration for the HALORA backend."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _bool_env(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _csv_env(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    """Small dependency-free settings object backed by environment variables."""

    app_name: str = os.getenv("HALORA_APP_NAME", "HALORA")
    app_version: str = os.getenv("HALORA_APP_VERSION", "1.0.0")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")

    
    perma_api_key: str | None = os.getenv("PERMA_API_KEY")
    ia_access_key: str | None = os.getenv("IA_ACCESS_KEY")
    ia_secret_key: str | None = os.getenv("IA_SECRET_KEY")
    urlhealth_user_agent: str = os.getenv(
        "URLHEALTH_USER_AGENT",
        "HALORA-URLHealth/1.0 (+https://example.com/contact)",
    )
    urlhealth_timeout: float = float(os.getenv("URLHEALTH_TIMEOUT", "10"))
    urlhealth_archive_order: list[str] = _csv_env(
        "URLHEALTH_ARCHIVE_ORDER", "perma,wayback,arquivo,memento"
    )
    urlhealth_cache_ttl: int = int(os.getenv("URLHEALTH_CACHE_TTL", "3600"))
    urlhealth_max_workers: int = int(os.getenv("URLHEALTH_MAX_WORKERS", "8"))
    urlhealth_max_batch: int = int(os.getenv("URLHEALTH_MAX_BATCH", "50"))
    # Only enable for local testing; disables the SSRF private-IP guard.
    urlhealth_allow_private: bool = _bool_env("URLHEALTH_ALLOW_PRIVATE", False)

    cors_origins: list[str] = _csv_env(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
