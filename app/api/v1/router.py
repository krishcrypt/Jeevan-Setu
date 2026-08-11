"""
Aggregates all v1 endpoint routers into a single APIRouter.

To add a new endpoint module later: create app/api/v1/endpoints/<name>.py
with its own `router = APIRouter()`, then include it below.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import chat, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(chat.router, tags=["Chat"])

# Future routers (uncomment/add when ready):
# from app.api.v1.endpoints import auth
# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
#
# from app.api.v1.endpoints import whatsapp
# api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
