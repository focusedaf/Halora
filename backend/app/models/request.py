"""Request models exposed by the HALORA API."""

from pydantic import BaseModel, Field


class ResponseVerificationRequest(BaseModel):
    response: str = Field(
        ...,
        min_length=1,
        description="Complete AI-generated response including references.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of evidence passages to retrieve.",
    )
