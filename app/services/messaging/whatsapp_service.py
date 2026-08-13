"""
M3 (WhatsApp integration) point.

Typical shape once implemented:
  - `verify_webhook(...)` for the WhatsApp Cloud API handshake
  - `parse_incoming_message(payload: dict) -> ChatRequest`
  - `send_whatsapp_message(to: str, text: str) -> None`

A dedicated router (app/api/v1/endpoints/whatsapp.py) should be added
and registered in app/api/v1/router.py when this is ready. It can reuse
`app.schemas.chat.ChatRequest/ChatResponse` and call
`app.services.ai.chatbot_service.get_ai_response` directly.
"""

def send_whatsapp_message(to: str, text: str) -> None:
    """Not implemented yet - see module docstring."""
    raise NotImplementedError("WhatsApp integration (M3) not implemented yet.")
