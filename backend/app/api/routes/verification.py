"""Response verification API routes."""

import logging

from fastapi import APIRouter, HTTPException

from app.models.request import ResponseVerificationRequest
from app.services.pipeline import verify_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["verification"])


@router.post("/verify-response")
def verify_ai_response(request: ResponseVerificationRequest):
    try:
        return verify_response(
            response=request.response,
            top_k=request.top_k,
        )
    except Exception:
        logger.exception("HALORA response verification failed")
        raise HTTPException(
            status_code=500,
            detail="Response verification failed.",
        )