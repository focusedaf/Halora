"""Future chat/model interaction routes.

The current backend exposes citation/claim verification only. This module is
kept as the integration point for the Next.js model chat layer once that part
of HALORA is implemented.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["chat"])
