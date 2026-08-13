"""
JeevanSetu AI chatbot service.

Flow:
User question
    ↓
Emergency check
    ↓
RAG retrieves relevant disease information
    ↓
Gemini receives the retrieved information
    ↓
Gemini generates the final user-friendly response
"""

import logging

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.services.ai.rag_service import (
    find_diseases,
    create_contexts,
)


logger = logging.getLogger(__name__)

settings = get_settings()

_client: genai.Client | None = None


# ============================================================
# Base Gemini instructions
# ============================================================

BASE_SYSTEM_PROMPT = """
You are JeevanSetu AI, a public health information assistant.

Your job is to provide clear, useful, and safe health information
to the general public.

IMPORTANT SAFETY RULES:

- Do not diagnose the user.
- Do not tell the user that they definitely have a disease.
- If symptoms could match multiple conditions, explain that they
  can have multiple possible causes.
- Do not prescribe medicines.
- Do not provide individualized medication dosages.
- Use the JeevanSetu knowledge base as the primary source when
  relevant information has been retrieved.
- Never invent information that contradicts the knowledge base.
- If the knowledge base does not contain a specific answer,
  provide only general, safe health information and clearly
  distinguish it from information retrieved from the knowledge base.
- Recommend professional medical evaluation when symptoms are
  severe, persistent, worsening, or concerning.

RESPONSE STYLE:

- Be natural and conversational.
- Do not repeatedly introduce yourself.
- Do not repeatedly say "I am an AI" or "I am not a doctor".
- Do not start every response with "Hello! I am JeevanSetu AI".
- Give the useful health information first.
- Use short paragraphs or bullet points when helpful.
- Keep responses concise but informative.
- End with a short safety statement only when appropriate.

IMPORTANT:

The diseases retrieved by RAG are possible matches, NOT diagnoses.
Never say:
"You have dengue."
"You have malaria."
"You definitely have this disease."

Instead say:
"These symptoms can occur with dengue, malaria, and other conditions."
"""


# ============================================================
# Language instructions
# ============================================================

LANGUAGE_INSTRUCTIONS = {
    "en": """
Respond ONLY in English.
Use simple language that is easy for the general public to understand.
""",

    "hi": """
Respond ONLY in Hindi using Devanagari script.
Use simple Hindi that is easy for the general public to understand.
""",

    "mr": """
Respond ONLY in Marathi using Devanagari script.
Use simple Marathi that is easy for the general public to understand.
""",
}


DEFAULT_LANGUAGE = "en"


# ============================================================
# Gemini client
# ============================================================

def _get_client() -> genai.Client:
    """Create and cache the Gemini client."""

    global _client

    if _client is None:

        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Add it to your .env file or Render environment variables."
            )

        _client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    return _client


# ============================================================
# System prompt
# ============================================================

def _build_system_prompt(language: str) -> str:
    """Build the system prompt with language instructions."""

    language_instruction = LANGUAGE_INSTRUCTIONS.get(
        language,
        LANGUAGE_INSTRUCTIONS[DEFAULT_LANGUAGE],
    )

    return (
        BASE_SYSTEM_PROMPT
        + "\n\n"
        + language_instruction
    )


# ============================================================
# Emergency detection
# ============================================================

_EMERGENCY_KEYWORDS = (
    "emergency",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "difficulty in breathing",
    "trouble breathing",
    "shortness of breath",
    "chest pain",
    "unconscious",
    "severe bleeding",
    "suicide",
    "heart attack",
)


def detect_emergency(message: str) -> bool:
    """
    Basic emergency keyword detection.

    This is a simple safety layer and should not be considered
    a complete medical triage system.
    """

    lowered = message.lower()

    return any(
        keyword in lowered
        for keyword in _EMERGENCY_KEYWORDS
    )


# ============================================================
# Main chatbot function
# ============================================================

def get_ai_response(
    message: str,
    language: str = DEFAULT_LANGUAGE,
    session_id: str | None = None,
) -> str:
    """
    Generate a final JeevanSetu response.

    The disease knowledge base is retrieved first.
    Gemini then generates a natural-language answer using
    the retrieved information.
    """

    # --------------------------------------------------------
    # Step 0: Emergency check
    # --------------------------------------------------------

    if detect_emergency(message):

        emergency_responses = {
            "en": (
                "Difficulty breathing or other severe symptoms can "
                "be a medical emergency. Please seek immediate "
                "medical help or go to the nearest hospital."
            ),

            "hi": (
                "सांस लेने में कठिनाई या अन्य गंभीर लक्षण "
                "चिकित्सीय आपातकाल हो सकते हैं। कृपया तुरंत "
                "चिकित्सीय सहायता लें या नजदीकी अस्पताल जाएं।"
            ),

            "mr": (
                "श्वास घेण्यास त्रास किंवा इतर गंभीर लक्षणे "
                "ही वैद्यकीय आपत्कालीन स्थिती असू शकते. "
                "कृपया त्वरित वैद्यकीय मदत घ्या किंवा जवळच्या "
                "रुग्णालयात जा."
            ),
        }

        return emergency_responses.get(
            language,
            emergency_responses["en"],
        )

    # --------------------------------------------------------
    # Step 1: Gemini client
    # --------------------------------------------------------

    client = _get_client()

    # --------------------------------------------------------
    # Step 2: System prompt
    # --------------------------------------------------------

    system_prompt = _build_system_prompt(language)

    # --------------------------------------------------------
    # Step 3: RAG retrieval
    #
    # Retrieve multiple possible matches rather than assuming
    # that the user's symptoms represent one disease.
    # --------------------------------------------------------

    matches = find_diseases(
        message,
        limit=3,
    )

    # --------------------------------------------------------
    # Step 4: Convert retrieved diseases to context
    # --------------------------------------------------------

    context = create_contexts(matches)

    # --------------------------------------------------------
    # Step 5: Build the Gemini prompt
    # --------------------------------------------------------

    if context:
        healthcare_context = context
    else:
        healthcare_context = (
            "No directly matching disease record was retrieved "
            "for this question."
        )

    prompt = f"""
USER QUESTION:
{message}


JEEVANSETU KNOWLEDGE BASE INFORMATION:
{healthcare_context}


HOW TO ANSWER:

1. Answer the user's actual question directly.

2. If knowledge-base information was retrieved, use it as the
   primary source for the answer.

3. If several diseases were retrieved, do NOT choose one as
   the user's diagnosis. Explain that the symptoms can occur
   in multiple conditions.

4. If the user names a disease directly, you may explain the
   disease using the retrieved knowledge-base information,
   but do not claim that the user actually has it.

5. If the user gives symptoms such as fever, headache, chills,
   cough, abdominal pain, etc., explain the relevant health
   information without diagnosing the user.

6. Do NOT say:
   "I do not have specific information in my knowledge base"
   unless the user specifically asks what is contained in the
   knowledge base.

7. If no matching knowledge-base information was retrieved,
   give a brief general health-information response instead.
   Do not pretend that the information came from the
   JeevanSetu knowledge base.

8. Do not invent disease-specific facts when no relevant
   knowledge-base information was retrieved.

9. Do not prescribe medication or give individualized doses.

10. If symptoms are severe, persistent, worsening, or
    concerning, recommend professional medical care.

11. Do not repeatedly say "I am an AI" or "I am not a doctor".
    A short statement such as "I can't diagnose the cause"
    is enough when a disclaimer is necessary.

12. Keep the response concise and useful.

13. Follow the requested language exactly.
"""

    # --------------------------------------------------------
    # Step 6: Gemini generates final response
    # --------------------------------------------------------

    response = client.models.generate_content(
        model=settings.AI_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=4000,
        ),
    )

    # --------------------------------------------------------
    # Step 7: Return final Gemini response
    # --------------------------------------------------------

    reply_text = (
        response.text or ""
    ).strip()

    if not reply_text:
        return (
            "Sorry, I couldn't generate a response. "
            "Please try again."
        )

    return reply_text