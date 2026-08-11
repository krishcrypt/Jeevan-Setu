"""
Data-access functions for the `sessions` and `chat_messages` collections.

Keeping all raw Motor queries in one place (rather than scattering them
across API endpoints) means the AI/RAG work (M1) and WhatsApp/SMS work
(M3) can call these same functions instead of re-implementing storage
logic.
"""

import logging
from datetime import datetime, timezone
from uuid import uuid4

from app.db.collections import CHAT_MESSAGES_COLLECTION, SESSIONS_COLLECTION
from app.db.mongodb import get_database
from app.models.chat_message import ChatMessageDocument
from app.models.session import SessionDocument

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def get_or_create_session(
    session_id: str | None,
    channel: str,
    language: str,
) -> SessionDocument:
    """
    Look up a session by id. If it doesn't exist (or none was given),
    create a new one. This doubles as the "users/sessions" collection
    required by M2 - there's no login yet, so a session is the closest
    thing we have to a "user" for now.

    On reuse, both `channel` and `language` are refreshed to reflect the
    most recent message - a user can switch languages mid-conversation
    and the session document (and every subsequent AI reply) follows.
    """
    db = get_database()
    sessions = db[SESSIONS_COLLECTION]

    if session_id:
        existing = await sessions.find_one({"session_id": session_id})
        if existing:
            await sessions.update_one(
                {"session_id": session_id},
                {"$set": {"last_active_at": _utcnow(), "channel": channel, "language": language}},
            )
            existing["last_active_at"] = _utcnow()
            existing["channel"] = channel
            existing["language"] = language
            return SessionDocument(**existing)

    new_session = SessionDocument(
        session_id=session_id or str(uuid4()),
        channel=channel,
        language=language,
        created_at=_utcnow(),
        last_active_at=_utcnow(),
    )
    await sessions.insert_one(new_session.model_dump())
    logger.info("Created new session %s", new_session.session_id)
    return new_session


async def save_chat_message(message: ChatMessageDocument) -> ChatMessageDocument:
    """Persist one chat exchange (incoming message + AI reply)."""
    db = get_database()
    await db[CHAT_MESSAGES_COLLECTION].insert_one(message.model_dump())
    return message


async def get_messages_for_session(session_id: str, limit: int = 50) -> list[dict]:
    """Fetch recent chat history for a session, most recent last."""
    db = get_database()
    cursor = (
        db[CHAT_MESSAGES_COLLECTION]
        .find({"session_id": session_id}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    messages = await cursor.to_list(length=limit)
    return list(reversed(messages))