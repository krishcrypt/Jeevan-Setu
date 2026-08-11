"""Pydantic schemas for the chat contract shared across web, WhatsApp, and SMS channels."""

import logging

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# Multilingual support: English, Hindi, Marathi.
SUPPORTED_LANGUAGES = {"en", "hi", "mr"}
DEFAULT_LANGUAGE = "en"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's incoming message text")
    session_id: str | None = Field(
        default=None, description="Conversation/session identifier, if any"
    )
    channel: str = Field(
        default="web", description="Origin channel: 'web' | 'whatsapp' | 'sms'"
    )
    language: str = Field(
        default=DEFAULT_LANGUAGE,
        description="Language code for the conversation: 'en' (English), 'hi' (Hindi), or 'mr' (Marathi)",
    )

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language(cls, value: str | None) -> str:
        """
        Backward-compatible language handling: normalize case/whitespace,
        and fall back to English for missing or unsupported codes instead
        of rejecting the request. This keeps older clients (and clients
        that never send a language at all) working unchanged.
        """
        if not value:
            return DEFAULT_LANGUAGE
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_LANGUAGES:
            logger.warning("Unsupported language '%s' requested - falling back to 'en'.", value)
            return DEFAULT_LANGUAGE
        return normalized


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Chatbot's reply text")
    session_id: str | None = None
    language: str = Field(default=DEFAULT_LANGUAGE, description="Language the reply was generated in")
    is_emergency: bool = Field(
        default=False, description="Naive keyword-based emergency flag (real triage comes with M1)"
    )