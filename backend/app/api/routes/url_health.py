"""URL health API routes."""

import logging

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.models.request import UrlHealthBatchRequest, UrlHealthRequest
from app.services.urlhealth import (
    check_text_urls,
    check_url_health,
    check_urls_health,
    extract_urls,
    list_providers,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/url-health", tags=["url-health"])


def _options(request) -> dict:
    return {
        "mode": request.mode,
        "providers": request.providers,
        "preserve": request.preserve,
        "refresh": request.refresh,
    }


@router.get("/providers")
def url_health_providers():
    """List the archive cascade in order, and which providers can save."""
    return {"status": "success", "providers": list_providers()}


@router.post("")
def url_health(request: UrlHealthRequest):
    """Waterfall health check for a single URL."""
    try:
        return {"status": "success", **check_url_health(request.url, **_options(request))}
    except Exception:
        logger.exception("URL health check failed")
        raise HTTPException(status_code=500, detail="URL health check failed.")


@router.post("/batch")
def url_health_batch(request: UrlHealthBatchRequest):
    """Waterfall health check for a list of URLs, or every URL found in text."""
    settings = get_settings()

    urls = request.urls or extract_urls(request.text)

    if len(urls) > settings.urlhealth_max_batch:
        raise HTTPException(
            status_code=422,
            detail=f"Too many URLs ({len(urls)}); the limit is {settings.urlhealth_max_batch}.",
        )

    try:
        if request.urls:
            return check_urls_health(request.urls, **_options(request))

        return check_text_urls(request.text, **_options(request))
    except Exception:
        logger.exception("URL health batch check failed")
        raise HTTPException(status_code=500, detail="URL health batch check failed.")
