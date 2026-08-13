"""
Centralized application settings.

Every module should read configuration from here instead of calling
os.getenv() directly. This makes it trivial to add new settings later
(AI model keys for M1, WhatsApp/SMS credentials for M3, DB URL, etc.)
without hunting through the codebase.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "JeevanSetu AI - Public Health Chatbot"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True

    # --- API ---
    API_V1_PREFIX: str = "/api/v1"

    # --- CORS ---
    # Comma-separated origins in .env, e.g. "http://localhost:3000,https://example.com"
    CORS_ORIGINS: str = "*"

    # --- Placeholders for future milestones (safe to leave blank for now) ---
    # M1 - AI/RAG integration (Google Gemini API)
    AI_MODEL_PROVIDER: str | None = "gemini"
    GEMINI_API_KEY: str | None = None
    # Google retires specific Gemini model IDs on a rolling basis (e.g.
    # gemini-2.5-flash is already blocked for new API keys as of Aug 2026).
    # "gemini-flash-latest" is Google's alias that always points at their
    # current recommended Flash model, so it survives these retirements
    # without a code/config change. Override in .env with a pinned model
    # id (e.g. gemini-3.6-flash) if you want reproducible behavior instead.
    AI_MODEL_NAME: str = "gemini-3.6-flash"
    VECTOR_DB_URL: str | None = None

    # M3 - WhatsApp / SMS integration
    WHATSAPP_API_TOKEN: str | None = None
    WHATSAPP_PHONE_NUMBER_ID: str | None = None
    SMS_GATEWAY_API_KEY: str | None = None

    # --- MongoDB (M2 - Backend) ---
    # Full connection URI, e.g.:
    #   local:  mongodb://localhost:27017
    #   Atlas:  mongodb+srv://<user>:<password>@<cluster>.mongodb.net
    # Never hardcode credentials - always read from the environment/.env.
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "jeevansetu"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance - import and call this, don't instantiate Settings() directly."""
    return Settings()