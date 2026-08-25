"""FastAPI application — MeetMind backend."""
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MeetMind starting up", env=settings.app_env)

    # Create DB tables — non-fatal if it fails
    try:
        from app.db.models import create_tables
        await create_tables()
        logger.info("Database tables ready")
    except Exception as e:
        logger.warning("DB init skipped (will retry on first request)", error=str(e))

    yield
    logger.info("MeetMind shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="MeetMind API",
        description="Agentic AI Meeting Assistant",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — allow frontend on any port
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request timing
    @app.middleware("http")
    async def add_process_time(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"
        return response

    # ── Health check ────────────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health():
        return {"status": "healthy", "app": settings.app_name, "env": settings.app_env}

    @app.get("/", tags=["System"])
    async def root():
        return {"message": "MeetMind API is running", "docs": "/docs"}

    # ── Routers (each wrapped so one bad import won't crash all) ─
    try:
        from app.api.meetings import router as meetings_router
        app.include_router(meetings_router, prefix="/api/meetings", tags=["Meetings"])
        logger.info("Meetings router loaded")
    except Exception as e:
        logger.warning("Meetings router skipped", error=str(e))

    try:
        from app.api.approvals import router as approvals_router
        app.include_router(approvals_router, prefix="/api/approvals", tags=["Approvals"])
        logger.info("Approvals router loaded")
    except Exception as e:
        logger.warning("Approvals router skipped", error=str(e))

    try:
        from app.api.integrations import router as integrations_router
        app.include_router(integrations_router, prefix="/api/integrations", tags=["Integrations"])
        logger.info("Integrations router loaded")
    except Exception as e:
        logger.warning("Integrations router skipped", error=str(e))

    try:
        from app.api.analytics import router as analytics_router
        app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
        logger.info("Analytics router loaded")
    except Exception as e:
        logger.warning("Analytics router skipped", error=str(e))

    try:
        from app.api.ask import router as ask_router
        app.include_router(ask_router, prefix="/api/ask", tags=["Ask"])
        logger.info("Ask router loaded")
    except Exception as e:
        logger.warning("Ask router skipped", error=str(e))

    # Global error handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled error", path=str(request.url), error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )

    return app


app = create_app()