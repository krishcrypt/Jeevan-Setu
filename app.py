import os
from pathlib import Path

import httpx
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from faster_whisper import WhisperModel


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).parent

M2_CHAT_URL = os.getenv(
    "M2_CHAT_URL",
    "http://127.0.0.1:8000/api/v1/chat"
)

# Whisper model
# "base" is a good balance for a prototype.
# For better accuracy, you can later use "small".
WHISPER_MODEL_SIZE = os.getenv(
    "WHISPER_MODEL_SIZE",
    "base"
)


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="JeevanSetu AI — M3 Chat Prototype",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static"
)


# ============================================================
# Load Whisper
# ============================================================

print(
    f"Loading Whisper model: {WHISPER_MODEL_SIZE}"
)

whisper_model = WhisperModel(
    WHISPER_MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)

print("Whisper model loaded successfully.")


# ============================================================
# Request Model
# ============================================================

class ChatRequest(BaseModel):
    user_id: str = Field(
        min_length=1,
        max_length=100
    )

    message: str = Field(
        min_length=1,
        max_length=2000
    )

    language: str | None = None

    channel: str = "web"


# ============================================================
# Home
# ============================================================

@app.get(
    "/",
    include_in_schema=False
)
async def home():

    return FileResponse(
        BASE_DIR / "static" / "index.html"
    )


# ============================================================
# Health
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "M3",
        "m2_chat_url": M2_CHAT_URL,
        "whisper_model": WHISPER_MODEL_SIZE
    }


# ============================================================
# Text Language Detection
# ============================================================

def detect_text_language(message: str) -> str:

    text = message.strip().lower()

    if not text:
        return "en"

    # Marathi-specific words
    marathi_words = [
        "डोकेदुखी",
        "अंगदुखी",
        "पोटदुखी",
        "खोकला",
        "मळमळ",
        "उलटी",
        "जुलाब",
        "ताप",
        "चक्कर",
        "थकवा",
        "श्वास",
        "छातीत",
        "दुखत",
        "दुखणे",
        "लसीकरण",
        "लस",
        "लक्षणे",
        "आरोग्य",
        "तपासणी",
        "औषध",
        "रुग्णालय",
        "मला",
        "माझा",
        "माझी",
        "माझे",
        "माझ्या",
        "आहे",
        "आहेत",
        "काय",
        "कसे",
        "कशी",
        "कधी",
        "कुठे",
        "माहिती",
        "सांगा",
        "करावे",
        "प्रतिबंध",
        "उद्रेक",
        "बचाव"
    ]

    if any(
        word in text
        for word in marathi_words
    ):
        return "mr"

    # Hindi-specific words
    hindi_words = [
        "मुझे",
        "मेरा",
        "मेरी",
        "मेरे",
        "क्या",
        "कैसे",
        "कैसी",
        "कब",
        "कहाँ",
        "क्यों",
        "बताएं",
        "बताइए",
        "जानकारी",
        "लक्षण",
        "बुखार",
        "सिरदर्द",
        "पेट दर्द",
        "खांसी",
        "उल्टी",
        "दस्त",
        "टीका",
        "टीकाकरण",
        "रोकथाम",
        "बचाव",
        "स्वास्थ्य",
        "डॉक्टर",
        "अस्पताल",
        "दर्द"
    ]

    if any(
        word in text
        for word in hindi_words
    ):
        return "hi"

    # Devanagari fallback
    if any(
        "\u0900" <= char <= "\u097F"
        for char in text
    ):
        return "hi"

    return "en"


# ============================================================
# M3 → M2
# ============================================================

@app.post("/api/chat")
async def relay_chat(
    payload: ChatRequest
):

    detected_language = (
        payload.language
        if payload.language in {"en", "hi", "mr"}
        else detect_text_language(
            payload.message
        )
    )

    m2_payload = {
        "message": payload.message,
        "session_id": payload.user_id,
        "channel": payload.channel,
        "language": detected_language
    }

    try:

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.post(
                M2_CHAT_URL,
                json=m2_payload
            )

            response.raise_for_status()

            data = response.json()

    except httpx.ConnectError:

        return {
            "response": offline_response(
                detected_language
            ),
            "language": detected_language,
            "category": "general",
            "safety_level": "warning",
            "source": "fallback",
            "error": "Could not connect to M2."
        }

    except httpx.HTTPStatusError as error:

        return {
            "response": offline_response(
                detected_language
            ),
            "language": detected_language,
            "category": "general",
            "safety_level": "warning",
            "source": "fallback",
            "error": (
                f"M2 returned HTTP "
                f"{error.response.status_code}"
            )
        }

    except httpx.HTTPError as error:

        return {
            "response": offline_response(
                detected_language
            ),
            "language": detected_language,
            "category": "general",
            "safety_level": "warning",
            "source": "fallback",
            "error": str(error)
        }

    reply = data.get(
        "reply",
        data.get(
            "response",
            "No response was received from M2."
        )
    )

    response_language = data.get(
        "language",
        detected_language
    )

    is_emergency = data.get(
        "is_emergency",
        False
    )

    return {
        "response": reply,
        "language": response_language,
        "category": "health",
        "safety_level": (
            "emergency"
            if is_emergency
            else "normal"
        ),
        "source": "m2",
        "session_id": data.get(
            "session_id",
            payload.user_id
        )
    }


# ============================================================
# Voice → Whisper → M2
# ============================================================

@app.post("/api/voice")
async def voice_chat(
    audio: UploadFile = File(...)
):

    temp_path = (
        BASE_DIR /
        "_voice_input.webm"
    )

    try:

        # ----------------------------------------------------
        # Save uploaded audio
        # ----------------------------------------------------

        audio_bytes = await audio.read()

        if not audio_bytes:
            return {
                "error": "No audio was received."
            }

        temp_path.write_bytes(
            audio_bytes
        )


        # ----------------------------------------------------
        # Whisper transcription
        # ----------------------------------------------------

        segments, info = (
            whisper_model.transcribe(
                str(temp_path),
                beam_size=5,
                vad_filter=True
            )
        )


        transcript = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()


        if not transcript:

            return {
                "error":
                    "Could not understand the audio."
            }


        # ----------------------------------------------------
        # Whisper language detection
        # ----------------------------------------------------

        whisper_language = (
            info.language or "en"
        ).lower()


        # Whisper may return:
        # en = English
        # hi = Hindi
        # mr = Marathi
        #
        # Other languages are mapped to English for now.

        if whisper_language not in {
            "en",
            "hi",
            "mr"
        }:
            detected_language = (
                detect_text_language(
                    transcript
                )
            )
        else:
            detected_language = (
                whisper_language
            )


        # ----------------------------------------------------
        # Send transcription to M2
        # ----------------------------------------------------

        m2_payload = {
            "message": transcript,
            "session_id": "voice-user",
            "channel": "web",
            "language": detected_language
        }


        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.post(
                M2_CHAT_URL,
                json=m2_payload
            )

            response.raise_for_status()

            data = response.json()


        reply = data.get(
            "reply",
            data.get(
                "response",
                "No response was received from M2."
            )
        )


        response_language = data.get(
            "language",
            detected_language
        )


        is_emergency = data.get(
            "is_emergency",
            False
        )


        return {
            "transcript": transcript,
            "language": response_language,
            "response": reply,
            "category": "health",
            "safety_level": (
                "emergency"
                if is_emergency
                else "normal"
            ),
            "source": "m2"
        }


    except httpx.HTTPError as error:

        return {
            "error":
                f"M2 API error: {error}"
        }

    except Exception as error:

        return {
            "error":
                f"Voice processing failed: {error}"
        }

    finally:

        if temp_path.exists():

            try:
                temp_path.unlink()

            except OSError:
                pass


# ============================================================
# Offline fallback
# ============================================================

def offline_response(
    language: str
) -> str:

    messages = {

        "en": (
            "The M2 backend is currently unavailable. "
            "Please start the M2 backend and try again."
        ),

        "hi": (
            "M2 बैकएंड अभी उपलब्ध नहीं है। "
            "कृपया M2 बैकएंड शुरू करके फिर प्रयास करें।"
        ),

        "mr": (
            "M2 बॅकएंड सध्या उपलब्ध नाही. "
            "कृपया M2 बॅकएंड सुरू करून पुन्हा प्रयत्न करा."
        )
    }

    return messages.get(
        language,
        messages["en"]
    )   