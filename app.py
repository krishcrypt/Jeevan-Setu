import os
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).parent
M2_CHAT_URL = os.getenv("M2_CHAT_URL", "http://127.0.0.1:8000/chat")

app = FastAPI(title="JeevanSetu AI — M3 Chat Prototype")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)
    language: str = Field(pattern="^(en|hi|mr)$")
    channel: str = "whatsapp"


@app.get("/", include_in_schema=False)
async def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "m2_chat_url": M2_CHAT_URL}


@app.post("/api/chat")
async def relay_chat(payload: ChatRequest):
    """M3 relay: sends a WhatsApp-style message to M2's /chat API."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(M2_CHAT_URL, json=payload.model_dump())
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as error:
        return {
            "response": offline_response(payload.language),
            "language": payload.language,
            "category": "general",
            "safety_level": "warning",
            "source": "fallback",
            "error": f"M2 API unavailable: {error}",
        }

    return {
        "response": data.get("response", data.get("reply", "No response was received.")),
        "language": data.get("language", payload.language),
        "category": data.get("category", "general"),
        "safety_level": data.get("safety_level", "normal"),
        "source": "m2",
    }


def offline_response(language: str) -> str:
    messages = {
        "en": "The M2 backend is currently unavailable. Please start it and try again. If this is a medical emergency, call 112 or seek urgent medical care.",
        "hi": "M2 बैकएंड अभी उपलब्ध नहीं है। कृपया इसे शुरू करके फिर प्रयास करें। चिकित्सा आपातस्थिति में 112 पर कॉल करें या तुरंत चिकित्सा सहायता लें।",
        "mr": "M2 बॅकएंड सध्या उपलब्ध नाही. कृपया तो सुरू करून पुन्हा प्रयत्न करा. वैद्यकीय आणीबाणी असल्यास 112 वर कॉल करा किंवा तातडीची वैद्यकीय मदत घ्या.",
    }
    return messages[language]
