"""
Chat endpoint.

This defines the request/response contract that the rest of the team
will build against:
  - M1 (AI/RAG): app.services.ai.chatbot_service.get_ai_response calls
    the real Google Gemini API (no retrieval/RAG yet), responding in
    the language requested (English, Hindi, or Marathi).
  - M3 (WhatsApp/SMS) will call this same endpoint (or the underlying
    service function directly) from their webhook handlers.

Every request/response pair is persisted to MongoDB via
app.db.repository, along with session, language, channel, and a naive
emergency flag - unchanged from before.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from app.db.repository import get_or_create_session, save_chat_message
from app.models.chat_message import ChatMessageDocument
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai.chatbot_service import detect_emergency, get_ai_response

logger = logging.getLogger(__name__)

router = APIRouter()

_FALLBACK_REPLY = (
    "Sorry, I'm unable to generate a response right now. "
    "Please try again in a moment, or consult a healthcare professional "
    "if this is urgent."
)


@router.post("/chat", response_model=ChatResponse, summary="Send a chat message")
async def send_message(payload: ChatRequest) -> ChatResponse:
    """
    Chat endpoint backed by MongoDB storage and a real, multilingual AI
    response.

    `payload.language` has already been normalized to one of "en" | "hi"
    | "mr" by ChatRequest's validator (unsupported/missing values fall
    back to "en"), so it's safe to pass straight through here.

    The Gemini SDK call is blocking, so it's run in a threadpool to
    avoid stalling the event loop. If the AI call fails for any reason
    (missing key, network/API error), we log it and fall back to a
    safe message rather than returning a 500 - the exchange is still
    saved to MongoDB either way.
    """
    session = await get_or_create_session(
        session_id=payload.session_id,
        channel=payload.channel,
        language=payload.language,
    )

    try:
        reply = await run_in_threadpool(
            get_ai_response, payload.message, payload.language, session.session_id
        )
    except Exception:
        logger.exception("AI response generation failed for session %s", session.session_id)
        reply = _FALLBACK_REPLY

    is_emergency = detect_emergency(payload.message)

    message_doc = ChatMessageDocument(
        session_id=session.session_id,
        channel=payload.channel,
        language=payload.language,
        incoming_message=payload.message,
        ai_response=reply,
        is_emergency=is_emergency,
        timestamp=datetime.now(timezone.utc),
    )
    await save_chat_message(message_doc)

    return ChatResponse(
        reply=reply,
        session_id=session.session_id,
        language=payload.language,
        is_emergency=is_emergency,
    )