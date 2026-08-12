"""
Central place to read environment variables.

Nothing else in the app should call os.environ directly - everything
goes through this Settings object so there is exactly one place that
knows how configuration is loaded.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file (backend/app/core/config.py -> backend/.env)
# rather than relative to the current working directory.
ENV_FILE_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    # Supabase Postgres connection string
    database_url: str

    # Path to the Firebase service-account JSON file (never committed to git)
    firebase_service_account_path: str

    # Comma-separated origins allowed to call this API during development
    frontend_origins: str = "http://localhost:3000"

    environment: str = "development"

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding="utf-8")

    @property
    def frontend_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


# This is the object every other module imports:
#   from app.core.config import settings
settings = Settings()

# If the Firebase service account path in the environment is relative, make it
# absolute relative to the backend folder (the directory containing the .env
# we load). This ensures code that opens the file works whether the app is
# started from the repo root or the backend folder.
try:
    _firebase_path = Path(settings.firebase_service_account_path or "")
    if _firebase_path and not _firebase_path.is_absolute():
        settings.firebase_service_account_path = str((ENV_FILE_PATH.parent / _firebase_path).resolve())
except Exception:
    # Be conservative: if something goes wrong here, leave the original value
    # so the usual error surfaces later (missing/invalid path).
    pass
