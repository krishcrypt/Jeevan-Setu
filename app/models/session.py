"""
Document schema for the `sessions` collection.

Represents a conversation session. There's no authentication yet, so
this is currently the closest thing to a "user" record - it's keyed by
a generated session_id rather than a login identity. When auth is added
later, a `user_id` field can be added here without changing the shape
chat_message.py depends on.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SessionDocument(BaseModel):
    session_id: str = Field(..., description="Unique session identifier (UUID)")
    channel: str = Field(default="web", description="'web' | 'whatsapp' | 'sms'")
    language: str = Field(default="en", description="Preferred language code, e.g. 'en', 'hi'")
    created_at: datetime
    last_active_at: datetime

    # Reserved for later milestones - safe to ignore for now.
    user_id: str | None = Field(default=None, description="Set once auth (future) is added")
    phone_number: str | None = Field(default=None, description="Set by M3 for WhatsApp/SMS")