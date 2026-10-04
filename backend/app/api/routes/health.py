"""Health and service metadata routes."""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/")
def root() -> dict[str, str]:
    settings = get_settings()

    return {
        "status": "online",
        "service": settings.app_name,
        "version": settings.app_version,
        "mode": "full_response_verification",
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}