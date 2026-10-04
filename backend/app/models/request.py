"""Request models exposed by the HALORA API."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


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


class _UrlHealthOptions(BaseModel):
    mode: Literal["first_hit", "all"] = Field(
        default="first_hit",
        description="first_hit stops at the first archive with a snapshot; all queries every archive.",
    )
    providers: list[str] | None = Field(
        default=None,
        description="Override the archive cascade order, e.g. ['wayback', 'perma'].",
    )
    preserve: bool = Field(
        default=False,
        description="If the page is live but unarchived, ask an archive to capture it.",
    )
    refresh: bool = Field(default=False, description="Bypass the result cache.")


class UrlHealthRequest(_UrlHealthOptions):
    url: str = Field(..., min_length=1, max_length=2048)


class UrlHealthBatchRequest(_UrlHealthOptions):
    urls: list[str] | None = Field(default=None, max_length=200)
    text: str | None = Field(
        default=None,
        description="Free text (e.g. an AI response); URLs are extracted automatically.",
    )

    @model_validator(mode="after")
    def _need_input(self):
        if not self.urls and not self.text:
            raise ValueError("Provide either 'urls' or 'text'.")
        return self
