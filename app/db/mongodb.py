"""
MongoDB connection management using Motor (the async MongoDB driver).

Usage pattern:
    - `connect_to_mongo()` / `close_mongo_connection()` are called from
      app startup/shutdown events in app/main.py.
    - Anywhere else in the app, import `get_database()` to get a handle
      to the active database and read/write collections from it.

Kept intentionally simple (a single module-level client) - this is a
hackathon prototype, not a production connection-pooling setup.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MongoDB:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    """Create the Motor client. Called once on app startup."""
    logger.info("Connecting to MongoDB at %s ...", settings.MONGODB_URI)
    mongodb.client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5000,  # fail fast instead of hanging
    )
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]
    logger.info("MongoDB client created for database '%s'.", settings.MONGODB_DB_NAME)


async def close_mongo_connection() -> None:
    """Close the Motor client. Called once on app shutdown."""
    if mongodb.client is not None:
        mongodb.client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """
    Return the active database handle.

    Raises a clear error if used before startup has run (e.g. in a
    script or test that doesn't go through the FastAPI lifecycle).
    """
    if mongodb.db is None:
        raise RuntimeError(
            "MongoDB is not connected yet. Make sure the app startup "
            "event (connect_to_mongo) has run."
        )
    return mongodb.db


async def ping_database() -> bool:
    """Lightweight connectivity check used by the /health/db endpoint."""
    if mongodb.client is None:
        return False
    try:
        await mongodb.client.admin.command("ping")
        return True
    except Exception:  # noqa: BLE001 - any failure means "not healthy"
        logger.exception("MongoDB ping failed.")
        return False