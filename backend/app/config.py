"""Application configuration and environment settings."""

import os
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Gokul's Astrological Insights API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # CORS configuration - default to local Next.js frontend; override via env
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

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
        self.debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")


settings = Settings()
