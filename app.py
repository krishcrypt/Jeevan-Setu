import os
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).parent

# Real M2 Backend API
#
# Default:
# http://127.0.0.1:8000/api/v1/chat
#
# You can override this using:
# M2_CHAT_URL=http://127.0.0.1:8000/api/v1/chat
#
M2_CHAT_URL = os.getenv(
    "M2_CHAT_URL",
    "http://127.0.0.1:8000/api/v1/chat"
)


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="JeevanSetu AI — M3 Chat Prototype",
    version="1.0.0"
)


# Serve frontend
app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static"
)


# ============================================================
# M3 Request Model
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

    language: str = Field(
        pattern="^(en|hi|mr)$"
    )

    channel: str = Field(
        default="web"
    )


# ============================================================
# Home Page
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
# M3 Health Check
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "M3",
        "m2_chat_url": M2_CHAT_URL
    }


# ============================================================
# M3 → M2 Chat Relay
# ============================================================

@app.post("/api/chat")
async def relay_chat(
    payload: ChatRequest
):

    """
    M3 receives the request from the frontend
    and forwards it to the real M2 backend.

    M2 endpoint:
        POST /api/v1/chat

    M2 request format:
        {
            "message": "...",
            "session_id": "...",
            "channel": "...",
            "language": "en|hi|mr"
        }

    M2 response format:
        {
            "reply": "...",
            "session_id": "...",
            "language": "...",
            "is_emergency": true/false
        }
    """

    # --------------------------------------------------------
    # Prepare request for M2
    # --------------------------------------------------------

    m2_payload = {
        "message": payload.message,

        # We use the browser user ID as the M2 session ID.
        "session_id": payload.user_id,

        # Pass the channel information.
        "channel": payload.channel,

        # Pass selected language.
        "language": payload.language
    }


    # --------------------------------------------------------
    # Call M2
    # --------------------------------------------------------

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


    except httpx.ConnectError as error:

        return {
            "response": offline_response(
                payload.language
            ),

            "language": payload.language,

            "category": "general",

            "safety_level": "warning",

            "source": "fallback",

            "error": (
                "Could not connect to M2. "
                "Make sure the M2 server is running on "
                "port 8000."
            )
        }


    except httpx.HTTPStatusError as error:

        return {
            "response": offline_response(
                payload.language
            ),

            "language": payload.language,

            "category": "general",

            "safety_level": "warning",

            "source": "fallback",

            "error": (
                f"M2 returned HTTP "
                f"{error.response.status_code}: "
                f"{error.response.text}"
            )
        }


    except httpx.HTTPError as error:

        return {
            "response": offline_response(
                payload.language
            ),

            "language": payload.language,

            "category": "general",

            "safety_level": "warning",

            "source": "fallback",

            "error": f"M2 API error: {error}"
        }


    except ValueError as error:

        return {
            "response": offline_response(
                payload.language
            ),

            "language": payload.language,

            "category": "general",

            "safety_level": "warning",

            "source": "fallback",

            "error": (
                f"M2 returned invalid JSON: {error}"
            )
        }


    # --------------------------------------------------------
    # Convert M2 response into M3 response
    # --------------------------------------------------------

    reply = data.get(
        "reply",
        data.get(
            "response",
            "No response was received from M2."
        )
    )

    response_language = data.get(
        "language",
        payload.language
    )

    is_emergency = data.get(
        "is_emergency",
        False
    )


    # --------------------------------------------------------
    # Determine safety level
    # --------------------------------------------------------

    if is_emergency:

        safety_level = "emergency"

    else:

        safety_level = "normal"


    # --------------------------------------------------------
    # Return response to frontend
    # --------------------------------------------------------

    return {

        "response": reply,

        "language": response_language,

        "category": "health",

        "safety_level": safety_level,

        "source": "m2",

        "session_id": data.get(
            "session_id",
            payload.user_id
        )
    }


# ============================================================
# Offline Fallback
# ============================================================

def offline_response(
    language: str
) -> str:

    messages = {

        "en": (
            "The M2 backend is currently unavailable. "
            "Please start the M2 backend and try again. "
            "If this is a medical emergency, call 112 "
            "or seek urgent medical care."
        ),

        "hi": (
            "M2 बैकएंड अभी उपलब्ध नहीं है। "
            "कृपया M2 बैकएंड शुरू करके फिर प्रयास करें। "
            "चिकित्सा आपातस्थिति में 112 पर कॉल करें "
            "या तुरंत चिकित्सा सहायता लें।"
        ),

        "mr": (
            "M2 बॅकएंड सध्या उपलब्ध नाही. "
            "कृपया M2 बॅकएंड सुरू करून पुन्हा प्रयत्न करा. "
            "वैद्यकीय आणीबाणी असल्यास 112 वर कॉल करा "
            "किंवा तातडीची वैद्यकीय मदत घ्या."
        )
    }

    return messages.get(
        language,
        messages["en"]
    )