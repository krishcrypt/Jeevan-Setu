"""Basic health/status endpoints used for uptime checks and demo purposes."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.db.mongodb import ping_database

router = APIRouter()
settings = get_settings()


@router.get("/health", summary="Liveness check")
def health_check():
    """Simple liveness probe - returns 200 if the server is up."""
    return {"status": "ok"}


@router.get("/ping", summary="Basic ping/pong")
def ping():
    return {"message": "pong"}


@router.get("/info", summary="Service metadata")
def info():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/db", summary="MongoDB connectivity check")
async def db_health_check():
    """Pings MongoDB and reports whether the connection is alive."""
    is_connected = await ping_database()
    return {
        "database": settings.MONGODB_DB_NAME,
        "connected": is_connected,
    }