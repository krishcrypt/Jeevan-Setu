"""
JeevanSetu AI - Public Health Chatbot
Application entrypoint (M2 - Backend).

Run with:
    uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.security.rate_limit import limiter
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup: open the MongoDB connection once for the whole app.
    await connect_to_mongo()
    yield
    # Shutdown: close it cleanly.
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for JeevanSetu AI, a public health chatbot (SIH project).",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
 _rate_limit_exceeded_handler,
)
app.add_middleware(SlowAPIMiddleware)

# CORS - open for hackathon/demo purposes; tighten before production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", summary="Root")
def root():
    return {
        "message": f"{settings.APP_NAME} backend is running.",
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
    }