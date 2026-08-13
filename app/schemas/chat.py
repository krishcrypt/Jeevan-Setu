"""Pydantic schemas for the chat contract shared across web, WhatsApp, and SMS channels."""

import logging
from typing import Literal

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# Multilingual support: English, Hindi, Marathi.
SUPPORTED_LANGUAGES = {"en", "hi", "mr"}
DEFAULT_LANGUAGE = "en"


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's incoming message text",
    )

    session_id: str | None = Field(
        default=None,
        max_length=100,
        description="Conversation/session identifier, if any",
    )

    channel: Literal["web", "whatsapp", "sms"] = Field(
        default="web",
        description="Origin channel",
    )

    language: str = Field(
        default=DEFAULT_LANGUAGE,
        max_length=10,
        description="Language code for the conversation",
    )

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language(cls, value: str | None) -> str:
        """
        Normalize language and fall back to English for unsupported codes.
        """
        if not value:
            return DEFAULT_LANGUAGE

        normalized = value.strip().lower()

        if normalized not in SUPPORTED_LANGUAGES:
            logger.warning(
                "Unsupported language '%s' requested - falling back to 'en'.",
                value,
            )
            return DEFAULT_LANGUAGE

        return normalized


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Chatbot's reply text")
    session_id: str | None = None
    language: str = Field(
        default=DEFAULT_LANGUAGE,
        description="Language the reply was generated in",
    )
    is_emergency: bool = Field(
        default=False,
        description="Naive keyword-based emergency flag (real triage comes with M1)",
    )