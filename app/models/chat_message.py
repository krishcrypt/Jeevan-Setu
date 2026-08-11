"""
Document schema for the `chat_messages` collection.

Stores one exchange per document: the user's incoming message plus the
chatbot's reply, along with metadata needed by later milestones
(language for M1, channel for M3, emergency flag for triage/alerts).
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageDocument(BaseModel):
    session_id: str = Field(..., description="Links this message to a SessionDocument")
    channel: str = Field(default="web", description="'web' | 'whatsapp' | 'sms'")
    language: str = Field(default="en", description="Language code of the conversation")

    incoming_message: str = Field(..., description="Raw text received from the user")
    ai_response: str = Field(..., description="Reply sent back (mock for now, real in M1)")

    is_emergency: bool = Field(
        default=False,
        description="Naive keyword-based flag for now; real triage logic comes with M1",
    )

    timestamp: datetime