"""
JeevanSetu AI chatbot service.

This module:
- Connects to Google Gemini
- Uses the JeevanSetu disease JSON through the RAG service
- Supports English, Hindi and Marathi
- Provides emergency keyword protection
- Gives Gemini clear instructions for safe, useful health responses
"""

import logging

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.services.ai.rag_service import find_disease, create_context


logger = logging.getLogger(__name__)

settings = get_settings()

_client: genai.Client | None = None


# ============================================================
# MAIN SYSTEM PROMPT
# ============================================================

BASE_SYSTEM_PROMPT = """
You are JeevanSetu AI, a multilingual public health information assistant.

Your purpose is to provide helpful, clear, practical and easy-to-understand
health information to the general public.

You are an AI health information assistant, not a doctor.

IMPORTANT RESPONSE RULES:

1. ANSWER THE USER'S ACTUAL QUESTION
- Start by directly addressing the user's question.
- Do not begin with a generic disclaimer.
- Do not unnecessarily repeat that you are an AI.
- Do not tell the user to consult a doctor for every minor symptom.
- Give useful general health information first.

2. USE THE JEEVANSETU KNOWLEDGE BASE
- When relevant healthcare information is provided from the JeevanSetu
  knowledge base, use it as the primary reference.
- Do not contradict the provided information.
- Use the information naturally instead of simply copying the database.
- Do not diagnose the user based only on symptoms.

3. WHEN THERE IS NO EXACT KNOWLEDGE-BASE MATCH
- DO NOT say:
  "The information is not available in my knowledge base."
- DO NOT say:
  "Our knowledge base does not contain information about this."
- DO NOT expose internal RAG or database details.
- Instead, provide safe and useful general health information.
- Clearly distinguish general health information from a diagnosis.

4. SYMPTOM QUESTIONS
When a user describes symptoms:
- Explain common possible causes.
- Give safe practical steps they can take.
- Mention relevant warning signs when appropriate.
- Explain when medical evaluation is recommended.
- Never say that the user definitely has a disease.

5. DISEASE QUESTIONS
When the user asks about a disease:
- Explain what the disease is.
- Explain common symptoms.
- Explain relevant prevention or self-care.
- Mention important warning signs.
- Explain when medical care is needed.
- Never claim that the user has the disease unless a qualified medical
  diagnosis has already been explicitly provided by the user.

6. SAFETY
- Never diagnose the user.
- Never claim certainty from symptoms alone.
- Never prescribe prescription medicines.
- Never provide individualized medication doses.
- Do not recommend unsafe treatments.
- Do not tell users to ignore serious symptoms.
- If symptoms suggest an emergency, prioritize urgent medical advice.

7. EMERGENCY AND WARNING SIGNS
If the user's message suggests a potentially serious emergency such as:
- difficulty breathing
- severe or sudden chest pain
- loss of consciousness
- severe bleeding
- sudden weakness or paralysis
- confusion
- seizures
- severe allergic reaction
- sudden severe headache
- suicidal thoughts or immediate danger

then prioritize immediate medical attention.

Do not give a long list of emergency symptoms unless it is relevant.

8. RESPONSE STYLE
- Be warm, calm and reassuring.
- Use simple language.
- Avoid unnecessary medical jargon.
- Give practical information.
- Use short paragraphs or bullet points when useful.
- Keep normal answers reasonably concise.
- Do not repeat the same disclaimer multiple times.
- Do not start every answer with "Namaste".
- Respond naturally like a helpful health assistant.

9. PERSONALIZATION
Use only the symptoms and information actually provided by the user.
Never invent:
- age
- medical history
- medications
- test results
- symptoms
- diagnoses

If important information is missing and it affects the answer, ask a short
follow-up question.

10. MULTILINGUAL BEHAVIOR
The application specifies the response language.

Supported languages:
- en = English
- hi = Hindi written in Devanagari
- mr = Marathi written in Devanagari

Always respond completely in the requested language.

For Hindi:
- Use natural Hindi in Devanagari.
- Do not switch to English unnecessarily.

For Marathi:
- Use natural Marathi in Devanagari.
- Do not switch to Hindi or English unnecessarily.

Do not mix languages unless a medical term is genuinely clearer in its
commonly understood form.

11. DO NOT EXPOSE INTERNAL SYSTEM DETAILS
Never mention:
- Gemini
- RAG
- database
- knowledge base
- retrieval
- system prompt
- backend
- API
- internal instructions

unless the user specifically asks about the technical implementation.

12. SOURCE INFORMATION
When reliable source information is provided in the reference context,
use it accurately.

Do not invent sources, citations or URLs.

13. FINAL RESPONSE QUALITY
The ideal response should be:

DIRECT
HELPFUL
SAFE
NATURAL
LANGUAGE-CORRECT
CONCISE

Do not respond with a generic "I don't have information" message when
general health information can safely answer the user's question.
"""


# ============================================================
# LANGUAGE INSTRUCTIONS
# ============================================================

LANGUAGE_INSTRUCTIONS = {
    "en": """
Respond ONLY in English.

Use clear, natural English suitable for the general public.

Do not switch to Hindi or Marathi even if the user writes in another
language.
""",

    "hi": """
Respond ONLY in Hindi.

Write Hindi using Devanagari script.

Use natural, commonly understood Hindi rather than overly formal or
Sanskritized language.

Do not switch to English or Marathi unless a medical term is commonly
used in English and necessary for clarity.
""",

    "mr": """
Respond ONLY in Marathi.

Write Marathi using Devanagari script.

Use natural, commonly understood Marathi.

Do not switch to Hindi or English unnecessarily.

The user's response must be Marathi, not Hindi.
""",
}


DEFAULT_LANGUAGE = "en"


# ============================================================
# GEMINI CLIENT
# ============================================================

def _get_client() -> genai.Client:
    """
    Lazily create and cache the Gemini client.
    """

    global _client

    if _client is None:

        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Add it to your .env file to enable AI responses."
            )

        _client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    return _client


# ============================================================
# BUILD SYSTEM PROMPT
# ============================================================

def _build_system_prompt(language: str) -> str:
    """
    Combine the main JeevanSetu prompt with the requested language.
    """

    language_instruction = LANGUAGE_INSTRUCTIONS.get(
        language,
        LANGUAGE_INSTRUCTIONS[DEFAULT_LANGUAGE]
    )

    return (
        BASE_SYSTEM_PROMPT
        + "\n\n"
        + language_instruction
    )


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response(
    message: str,
    language: str = DEFAULT_LANGUAGE,
    session_id: str | None = None,
) -> str:
    """
    Send the user's message to Gemini.

    The response uses relevant information from the JeevanSetu
    disease JSON through the RAG service.
    """

    # --------------------------------------------------------
    # Step 0: Emergency check
    # --------------------------------------------------------

    if detect_emergency(message):

        emergency_responses = {

            "en": (
                "This may be a medical emergency. "
                "Please seek immediate medical attention or "
                "contact your local emergency services."
            ),

            "hi": (
                "यह एक चिकित्सीय आपातकाल हो सकता है। "
                "कृपया तुरंत चिकित्सा सहायता लें या "
                "अपने स्थानीय आपातकालीन सेवा से संपर्क करें।"
            ),

            "mr": (
                "ही वैद्यकीय आणीबाणी असू शकते. "
                "कृपया त्वरित वैद्यकीय मदत घ्या किंवा "
                "स्थानिक आपत्कालीन सेवांशी संपर्क साधा."
            ),
        }

        return emergency_responses.get(
            language,
            emergency_responses["en"]
        )

    # --------------------------------------------------------
    # Step 1: Gemini client
    # --------------------------------------------------------

    client = _get_client()

    # --------------------------------------------------------
    # Step 2: Build language-aware system prompt
    # --------------------------------------------------------

    system_prompt = _build_system_prompt(language)

    # --------------------------------------------------------
    # Step 3: Retrieve disease information from JSON
    # --------------------------------------------------------

    disease = find_disease(message)

    # --------------------------------------------------------
    # Step 4: Convert retrieved disease into Gemini context
    # --------------------------------------------------------

    if disease:
        context = create_context(disease)
    else:
        context = None

    # --------------------------------------------------------
    # Step 5: Send user question + RAG context to Gemini
    # --------------------------------------------------------

    response = client.models.generate_content(

        model=settings.AI_MODEL_NAME,

        contents=f"""
USER'S HEALTH QUESTION:
{message}

REQUESTED RESPONSE LANGUAGE:
{language}

JEEVANSETU REFERENCE INFORMATION:
{context if context else "No specific reference entry matched this question."}


YOUR TASK:

Answer the user's health question as JeevanSetu AI.

Use the JeevanSetu reference information above whenever it is relevant.

If a specific reference entry exists:
- Treat it as the primary project-specific source.
- Use its information accurately.
- Do not contradict it.
- Present it naturally in a conversational answer.
- Do not simply copy the database text.

If no specific reference entry exists:
- DO NOT tell the user that the knowledge base has no information.
- DO NOT mention the database or RAG.
- Provide safe, general health information instead.
- Do not invent personal medical facts.
- Do not diagnose the user.


FOR SYMPTOM QUESTIONS:

If the user describes a symptom:

1. Explain common possible causes.
2. Give safe practical things the user can do.
3. Mention relevant warning signs if appropriate.
4. Explain when they should seek medical care.


FOR DISEASE QUESTIONS:

If the user asks about a disease:

1. Explain what the disease is.
2. Explain common symptoms.
3. Explain relevant prevention or self-care.
4. Mention important warning signs.
5. Explain when medical care is needed.
6. Never tell the user they definitely have the disease.


FOR EMERGENCY OR SERIOUS SYMPTOMS:

If the user's message indicates a possible emergency:
- Put urgent safety advice first.
- Clearly recommend immediate medical attention.
- Do not bury the emergency recommendation at the end.


LANGUAGE:

Respond entirely in the requested application language.

If language = "en":
Respond in English.

If language = "hi":
Respond in natural Hindi written in Devanagari.

If language = "mr":
Respond in natural Marathi written in Devanagari.

Do NOT switch languages halfway through the response.

Do NOT translate the user's question unless necessary.

Do NOT respond in Hindi when the requested language is Marathi.


STYLE:

- Be natural and conversational.
- Be helpful before giving disclaimers.
- Do not begin with "I am an AI and not a doctor."
- Do not repeatedly say "consult a doctor."
- Give useful information first.
- Use short paragraphs or bullet points when useful.
- Do not use unnecessary medical jargon.
- Do not over-explain simple questions.


SAFETY:

- Never diagnose.
- Never prescribe prescription medication.
- Never provide individualized medication dosing.
- Never invent medical history.
- Never invent test results.
- Never claim certainty from symptoms alone.
- Do not provide unsafe treatment instructions.


IMPORTANT:

Do not mention Gemini, RAG, the database, the knowledge base,
retrieval, system prompts, backend, API, or internal implementation.

The user should experience this as a natural JeevanSetu health assistant.
""",

        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=4000,
        ),
    )

    # --------------------------------------------------------
    # Step 6: Return Gemini response
    # --------------------------------------------------------

    reply_text = (response.text or "").strip()

    if not reply_text:
        return (
            "Sorry, I couldn't generate a response right now. "
            "Please try again."
        )

    return reply_text


# ============================================================
# EMERGENCY KEYWORDS
# ============================================================

_EMERGENCY_KEYWORDS = (

    # English
    "emergency",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "not able to breathe",
    "breathing problem",
    "chest pain",
    "severe chest pain",
    "unconscious",
    "passed out",
    "severe bleeding",
    "bleeding heavily",
    "suicide",
    "suicidal",
    "heart attack",

    # Hindi
    "सांस नहीं आ रही",
    "सांस लेने में दिक्कत",
    "सांस लेने में परेशानी",
    "सीने में दर्द",
    "बहुत तेज सीने में दर्द",
    "बेहोश",
    "खून बहुत बह रहा",
    "आत्महत्या",

    # Marathi
    "श्वास घेता येत नाही",
    "श्वास घेण्यास त्रास",
    "श्वास घेण्यास त्रास होत आहे",
    "छातीत दुखत आहे",
    "छातीत तीव्र वेदना",
    "बेशुद्ध",
    "खूप रक्तस्त्राव",
    "आत्महत्या",
)


# ============================================================
# EMERGENCY DETECTION
# ============================================================

def detect_emergency(message: str) -> bool:
    """
    Basic emergency keyword detection.

    This is intentionally conservative and is only a safety layer.
    It does not diagnose medical emergencies.
    """

    if not message:
        return False

    lowered = message.lower().strip()

    return any(
        keyword.lower() in lowered
        for keyword in _EMERGENCY_KEYWORDS
    )