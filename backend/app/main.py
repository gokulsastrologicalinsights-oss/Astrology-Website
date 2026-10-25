"""Gokul's Astrological Insights - FastAPI Application Entry Point.

Deterministic, rule-based Vedic and KP astrology backend powered by XALEN ephemeris.
Zero AI / LLM dependencies.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings

logger = logging.getLogger("gai.api")
from app.routers import (
    health,
    metadata,
    horoscope,
    dasa,
    kp,
    rules,
    admin,
    numerology,
    muhurta,
    vedic_extensions,
    kp_events,
    kp_prediction,
    vastu,
    remedies,
    pdf_reports,
    unified_prediction,
    marriage_compatibility,
    horoscope_writing,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown hooks."""
    import os
    if os.getenv("ADMIN_USERNAME") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        try:
            from app.bootstrap_admin import bootstrap_admin
            bootstrap_admin()
        except Exception:
            pass
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Deterministic Vedic & KP Astrology API powered by the XALEN astronomical engine. "
        "Strictly rule-based calculations without conversational AI or generative models."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 1. CORS Middleware - restricted to configured origins + Vercel preview/production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=settings.allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
)


# 2. Request body size limit middleware
@app.middleware("http")
async def limit_request_size_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.max_request_body_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "Request entity too large",
                        "detail": f"Max allowed size is {settings.max_request_body_bytes} bytes",
                    },
                )
        except ValueError:
            pass
    return await call_next(request)


# 3. Structured Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append({
            "field": loc,
            "message": err.get("msg"),
            "type": err.get("type"),
        })
    return JSONResponse(
        status_code=422,
        content={
            "error": "Input Validation Error",
            "detail": "One or more input fields failed validation constraints.",
            "validation_errors": errors,
        },
    )



# 4. Global fallback exception handler (no internal stack-trace leaks)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = str(uuid.uuid4())[:8]
    logger.exception(f"Unhandled exception [req_id={req_id}] on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": f"An unexpected error occurred during calculation. (Request ID: {req_id})",
            "request_id": req_id,
        },
    )


# 5. Root endpoint
@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "documentation": "/docs",
        "health": "/health",
        "metadata": f"{settings.api_prefix}/metadata",
    }


# 6. Include Routers
app.include_router(health.router)
app.include_router(metadata.router)
app.include_router(horoscope.router)
app.include_router(dasa.router)
app.include_router(kp.router)
app.include_router(rules.router)
app.include_router(admin.router)
app.include_router(numerology.router)
app.include_router(muhurta.router)
app.include_router(vedic_extensions.router)
app.include_router(kp_events.router)
app.include_router(kp_prediction.router)
app.include_router(vastu.router)
app.include_router(remedies.router)
app.include_router(pdf_reports.router)
app.include_router(pdf_reports.kp_router)
app.include_router(unified_prediction.router)
app.include_router(marriage_compatibility.router, prefix="/api/v1/marriage-compatibility")
app.include_router(marriage_compatibility.router, prefix="/api/marriage-compatibility")
app.include_router(horoscope_writing.router)


