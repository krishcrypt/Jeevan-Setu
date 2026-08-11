"""Temporary M2-style mock API for M3 integration testing.

Run this before the M3 chat app. Replace it with M2's real service later,
without changing the request/response contract.
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="JeevanSetu AI — Mock M2 API", version="1.0.0")


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=2000)
    language: str = Field(pattern="^(en|hi|mr)$")
    channel: str = Field(default="whatsapp")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "mock-m2-api"}


@app.post("/chat")
async def chat(payload: ChatRequest):
    category, safety = classify(payload.message)
    return {
        "response": message_for(category, safety, payload.language),
        "language": payload.language,
        "category": category,
        "safety_level": safety,
    }


def classify(message: str) -> tuple[str, str]:
    text = message.lower()
    emergency_words = ("chest pain", "can't breathe", "cannot breathe", "unconscious", "bleeding", "suicide", "severe", "सीने में दर्द", "सांस नहीं", "बेशुद्ध", "छातीत दुखणे", "श्वास")
    if any(word in text for word in emergency_words):
        return "emergency", "emergency"
    if any(word in text for word in ("vaccine", "vaccination", "टीका", "लसी")):
        return "vaccination", "normal"
    if any(word in text for word in ("outbreak", "alert", "outbreak", "प्रकोप", "उद्रेक")):
        return "outbreak", "warning"
    if any(word in text for word in ("prevent", "prevention", "बचाव", "प्रतिबंध")):
        return "prevention", "normal"
    return "disease", "normal"


def message_for(category: str, safety: str, language: str) -> str:
    responses = {
        "en": {
            "disease": "This is a mock health response. Common symptoms may include fever, headache, and body pain. Rest, drink fluids, and consult a qualified clinician if symptoms persist or worsen.",
            "prevention": "Mock prevention advice: wash hands, drink safe water, use mosquito protection where needed, and seek medical guidance for concerning symptoms.",
            "vaccination": "Mock vaccination response: please check the recommended schedule with a government health centre or qualified clinician; eligibility depends on age and local guidance.",
            "outbreak": "Mock health alert: follow official local public-health updates, use preventive measures, and visit a health centre if you develop concerning symptoms.",
            "emergency": "EMERGENCY: Please call 112 or go to the nearest emergency department immediately. Do not rely on this chat for urgent medical care.",
        },
        "hi": {
            "disease": "यह एक मॉक स्वास्थ्य उत्तर है। सामान्य लक्षणों में बुखार, सिरदर्द और बदन दर्द शामिल हो सकते हैं। आराम करें, तरल पदार्थ लें और लक्षण बने रहने या बढ़ने पर योग्य डॉक्टर से संपर्क करें।",
            "prevention": "मॉक बचाव सलाह: हाथ धोएं, सुरक्षित पानी पिएं, जरूरत होने पर मच्छरों से बचाव करें और चिंताजनक लक्षणों पर डॉक्टर से सलाह लें।",
            "vaccination": "मॉक टीकाकरण उत्तर: उम्र और स्थानीय दिशा-निर्देशों के अनुसार सरकारी स्वास्थ्य केंद्र या योग्य डॉक्टर से टीकाकरण का समय पूछें।",
            "outbreak": "मॉक स्वास्थ्य अलर्ट: स्थानीय स्वास्थ्य विभाग के आधिकारिक अपडेट देखें, बचाव के उपाय अपनाएं और चिंताजनक लक्षणों पर स्वास्थ्य केंद्र जाएं।",
            "emergency": "आपातस्थिति: तुरंत 112 पर कॉल करें या निकटतम आपात विभाग जाएं। तत्काल चिकित्सा सहायता के लिए इस चैट पर निर्भर न रहें।",
        },
        "mr": {
            "disease": "हे मॉक आरोग्य उत्तर आहे. सामान्य लक्षणांमध्ये ताप, डोकेदुखी आणि अंगदुखी असू शकते. विश्रांती घ्या, द्रवपदार्थ घ्या आणि लक्षणे कायम राहिल्यास किंवा वाढल्यास पात्र डॉक्टरांचा सल्ला घ्या.",
            "prevention": "मॉक प्रतिबंध सल्ला: हात धुवा, सुरक्षित पाणी प्या, गरजेनुसार डासांपासून बचाव करा आणि चिंताजनक लक्षणांसाठी डॉक्टरांचा सल्ला घ्या.",
            "vaccination": "मॉक लसीकरण उत्तर: वय आणि स्थानिक मार्गदर्शनानुसार सरकारी आरोग्य केंद्र किंवा पात्र डॉक्टरांकडून लसीकरण वेळापत्रक तपासा.",
            "outbreak": "मॉक आरोग्य इशारा: स्थानिक आरोग्य विभागाचे अधिकृत अद्यतन पहा, प्रतिबंधात्मक उपाय करा आणि चिंताजनक लक्षणे असल्यास आरोग्य केंद्रात जा.",
            "emergency": "आणीबाणी: तातडीने 112 वर कॉल करा किंवा जवळच्या आपत्कालीन विभागात जा. तातडीच्या वैद्यकीय मदतीसाठी या चॅटवर अवलंबून राहू नका.",
        },
    }
    return responses[language][category]
