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
from app.services.ai.rag_service import find_disease, create_context

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

def get_ai_response(
    message: str,
    language: str = DEFAULT_LANGUAGE,
    session_id: str | None = None,
) -> str:
    """
    Send the user's message to Gemini and return its reply text,
    using relevant healthcare information from the RAG system.
    """
    # Step 0: Check for emergency situations before calling Gemini
    if detect_emergency(message):
        emergency_responses = {
            "en": (
                "This may be a medical emergency. "
                "Please seek immediate medical attention or contact your local emergency services."
            ),
            "hi": (
                "यह एक चिकित्सीय आपातकाल हो सकता है। "
                "कृपया तुरंत चिकित्सा सहायता लें या स्थानीय आपातकालीन सेवाओं से संपर्क करें।"
            ),
            "mr": (
                "ही वैद्यकीय आपत्कालीन परिस्थिती असू शकते. "
                "कृपया त्वरित वैद्यकीय मदत घ्या किंवा स्थानिक आपत्कालीन सेवांशी संपर्क साधा."
            ),
        }

        return emergency_responses.get(
            language,
            emergency_responses["en"]
        )
    client = _get_client()
    system_prompt = _build_system_prompt(language)

    # Step 1: Retrieve relevant healthcare information from M4 data
    disease = find_disease(message)

    # Step 2: Convert the retrieved data into clean context
    if disease:
        context = create_context(disease)
    else:
        context = None

    # Step 3: Give the user's question + healthcare context to Gemini
    response = client.models.generate_content(
        model=settings.AI_MODEL_NAME,
        contents=f"""
User question:
{message}

Relevant healthcare information from the JeevanSetu knowledge base:
{context if context else "No specific information was found in the knowledge base."}

Instructions:
- Use the healthcare information above when answering.
- Do not invent medical facts that contradict the provided information.
- Do not diagnose the user.
- If the information is not available in the knowledge base, clearly say that.
""",
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