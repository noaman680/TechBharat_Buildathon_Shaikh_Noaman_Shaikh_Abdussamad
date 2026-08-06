"""FastAPI application factory for MeetMind."""
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api import meetings, approvals, integrations, analytics, ask
from app.db.models import create_tables

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("MeetMind starting up", env=settings.app_env)
    await create_tables()
    yield
    logger.info("MeetMind shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="MeetMind API",
        description="Agentic AI Meeting Assistant — transforms meetings into structured intelligence",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://meetmind.app"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        return response

    # Health check
    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "healthy", "app": settings.app_name, "env": settings.app_env}

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", path=request.url.path, error=str(exc))
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    # Routers
    app.include_router(meetings.router,     prefix="/api/meetings",      tags=["Meetings"])
    app.include_router(approvals.router,    prefix="/api/approvals",     tags=["Approvals"])
    app.include_router(integrations.router, prefix="/api/integrations",  tags=["Integrations"])
    app.include_router(analytics.router,    prefix="/api/analytics",     tags=["Analytics"])
    app.include_router(ask.router,          prefix="/api/ask",           tags=["Ask"])

    return app


app = create_app()
