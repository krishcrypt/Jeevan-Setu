"""
M1 (AI/RAG) integration point.

`get_ai_response` calls the Google Gemini API directly (no retrieval
yet - that's the "RAG" part of M1, still to be added: pull relevant
health documents/FAQs and pass them in as context before calling the
model).

Multilingual support: the reply language is controlled entirely by the
system prompt (see LANGUAGE_INSTRUCTIONS below), not by asking Gemini
to "detect" the language - this is what keeps it from randomly
switching languages mid-conversation regardless of what language the
user typed in.

This function raises on failure (missing API key, network/API error).
It intentionally does NOT swallow errors here - the caller
(app/api/v1/endpoints/chat.py) decides how to handle a failure, e.g.
falling back to a safe message so the API never breaks for the user.
"""

import logging

from google import genai
from google.genai import types

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: genai.Client | None = None

BASE_SYSTEM_PROMPT = (
    "You are JeevanSetu AI, a public health assistant chatbot built for "
    "a hackathon prototype (Smart India Hackathon). Answer health-related "
    "questions in clear, simple language suitable for the general public. "
    "You are not a doctor - never diagnose, and always recommend seeing a "
    "qualified medical professional for diagnosis, treatment, or anything "
    "urgent. Keep answers concise (a few sentences)."
)

# One explicit, strict instruction per supported language. This is
# appended to the base prompt so Gemini has a single unambiguous
# language directive instead of guessing from the user's message.
LANGUAGE_INSTRUCTIONS = {
    "en": (
        "Respond ONLY in English. Do not use any other language in your "
        "reply, even if the user writes in a different language."
    ),
    "hi": (
        "आपको केवल हिंदी में जवाब देना है (हिंदी लिपि/देवनागरी में लिखें)। "
        "उपयोगकर्ता किसी भी भाषा में लिखे, अपना जवाब हमेशा हिंदी में ही दें। "
        "किसी और भाषा का प्रयोग बिल्कुल न करें।\n"
        "(English: Respond ONLY in Hindi, written in Devanagari script. "
        "Regardless of what language the user writes in, always reply in "
        "Hindi only. Never switch to any other language.)"
    ),
    "mr": (
        "तुम्ही फक्त मराठीत उत्तर द्यायचे आहे (मराठी लिपी/देवनागरीत लिहा). "
        "वापरकर्ता कोणत्याही भाषेत लिहित असला तरी, तुमचे उत्तर नेहमी फक्त "
        "मराठीतच द्या. इतर कोणतीही भाषा वापरू नका.\n"
        "(English: Respond ONLY in Marathi, written in Devanagari script. "
        "Regardless of what language the user writes in, always reply in "
        "Marathi only. Never switch to any other language.)"
    ),
}

DEFAULT_LANGUAGE = "en"


def _get_client() -> genai.Client:
    """Lazily create and cache the Gemini client (needs GEMINI_API_KEY set)."""
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "(get a key from https://aistudio.google.com/apikey) to enable AI responses."
            )
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def _build_system_prompt(language: str) -> str:
    """Combine the base persona/safety prompt with a strict language directive."""
    language_instruction = LANGUAGE_INSTRUCTIONS.get(
        language, LANGUAGE_INSTRUCTIONS[DEFAULT_LANGUAGE]
    )
    return f"{BASE_SYSTEM_PROMPT}\n\n{language_instruction}"


def get_ai_response(message: str, language: str = DEFAULT_LANGUAGE, session_id: str | None = None) -> str:
    """
    Send the user's message to Gemini and return its reply text, in the
    requested language.

    `language` should already be normalized to one of "en" | "hi" | "mr"
    (app.schemas.chat.ChatRequest does this before it ever reaches here);
    any unrecognized value safely falls back to English.

    Raises RuntimeError / google.genai errors on failure - the /chat
    endpoint catches these and falls back to a safe message.
    """
    client = _get_client()
    system_prompt = _build_system_prompt(language)
    response = client.models.generate_content(
        model=settings.AI_MODEL_NAME,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=4000,
        ),
    )
    reply_text = (response.text or "").strip()
    return reply_text or "Sorry, I couldn't generate a response. Please try again."


# Naive placeholder so chat storage has a real (if crude) emergency flag
# to persist. M1 should replace this with proper symptom/triage logic.
_EMERGENCY_KEYWORDS = (
    "emergency",
    "can't breathe",
    "cannot breathe",
    "chest pain",
    "unconscious",
    "severe bleeding",
    "suicide",
    "heart attack",
)


def detect_emergency(message: str) -> bool:
    """Very simple keyword match - placeholder until M1 adds real triage."""
    lowered = message.lower()
    return any(keyword in lowered for keyword in _EMERGENCY_KEYWORDS)