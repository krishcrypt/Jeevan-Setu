"""
M3 (SMS integration) point.

Typical shape once implemented, e.g. using Twilio or an SMS gateway:
  - `send_sms(to: str, text: str) -> None`
  - `parse_incoming_sms(payload: dict) -> ChatRequest`

A dedicated router (app/api/v1/endpoints/sms.py) should be added and
registered in app/api/v1/router.py when this is ready.
"""

def send_sms(to: str, text: str) -> None:
    """Not implemented yet - see module docstring."""
    raise NotImplementedError("SMS integration (M3) not implemented yet.")
