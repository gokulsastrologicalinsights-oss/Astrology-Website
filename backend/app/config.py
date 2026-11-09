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

    # CORS configuration - supports local dev and production frontend domains
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://gai-astrology.com",
        "https://www.gai-astrology.com",
        "https://astrology-website.vercel.app",
    ]
    allowed_origin_regex: str | None = r"^https://.*\.vercel\.app$"

    # PDF storage configuration for high-concurrency offloading
    pdf_storage_bucket: str = "horoscope-reports"
    enable_pdf_storage_cache: bool = True

    # Security & limits
    max_request_body_bytes: int = 10_485_760  # 10 MB max request body (supports large Dasa trees & composite charts)
    rate_limit_per_minute: int = 60         # 60 requests/minute per client IP

    # Supported Ayanamsas (canonical IDs in XALEN)
    default_ayanamsa: int = 0  # Lahiri (Chitrapaksha)
    default_house_system: int = 2  # Placidus

    def __init__(self, **data):
        super().__init__(**data)
        env_origins = os.getenv("ALLOWED_ORIGINS")
        if env_origins:
            raw = env_origins.strip()
            if raw.startswith("[") and raw.endswith("]"):
                try:
                    import json
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        self.allowed_origins = [str(o).strip() for o in parsed if str(o).strip()]
                except Exception:
                    self.allowed_origins = [o.strip().strip("'\"[]") for o in raw.split(",") if o.strip().strip("'\"[]")]
            else:
                self.allowed_origins = [o.strip().strip("'\"") for o in raw.split(",") if o.strip().strip("'\"")]
        env_regex = os.getenv("ALLOWED_ORIGIN_REGEX")
        if env_regex is not None:
            self.allowed_origin_regex = env_regex if env_regex else None
        bucket = os.getenv("PDF_STORAGE_BUCKET")
        if bucket:
            self.pdf_storage_bucket = bucket.strip()
        env_body_limit = os.getenv("MAX_REQUEST_BODY_BYTES")
        if env_body_limit and env_body_limit.isdigit():
            self.max_request_body_bytes = int(env_body_limit)
        self.debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")


settings = Settings()
