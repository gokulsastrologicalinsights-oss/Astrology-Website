"""Application configuration and environment settings."""

import os
from typing import List
from pydantic import BaseModel


def _load_env_files():
    """Safely loads key-value pairs from .env and backend/.env without external dependencies."""
    base_dirs = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ]
    for bdir in base_dirs:
        for fname in [".env", "backend/.env", "frontend/.env.local"]:
            fpath = os.path.join(bdir, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                k, v = k.strip(), v.strip().strip("'\"")
                                if k and k not in os.environ:
                                    os.environ[k] = v
                except Exception:
                    pass


_load_env_files()


class Settings(BaseModel):
    app_name: str = "Gokul's Astrological Insights API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # CORS configuration - default to local Next.js frontend; override via env
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    allowed_origin_regex: str | None = r"^https://.*\.vercel\.app$"

    # Security & limits
    max_request_body_bytes: int = 1_048_576  # 1 MB max request body
    rate_limit_per_minute: int = 60         # 60 requests/minute per client IP

    # Supported Ayanamsas (canonical IDs in XALEN)
    default_ayanamsa: int = 0  # Lahiri (Chitrapaksha)
    default_house_system: int = 2  # Placidus

    def __init__(self, **data):
        super().__init__(**data)
        env_origins = os.getenv("ALLOWED_ORIGINS")
        if env_origins:
            self.allowed_origins = [o.strip() for o in env_origins.split(",") if o.strip()]
        env_regex = os.getenv("ALLOWED_ORIGIN_REGEX")
        if env_regex is not None:
            self.allowed_origin_regex = env_regex if env_regex else None
        self.debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")


settings = Settings()
