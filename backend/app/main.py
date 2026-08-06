from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import meetings, approvals, integrations, analytics, ask

app = FastAPI(
    title="MeetMind API",
    description="Agentic AI Meeting Assistant — see docs/BLUEPRINT.md",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENV == "development" else [],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meetings.router, prefix="/api/meetings", tags=["meetings"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["approvals"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ask.router, prefix="/api", tags=["memory"])


@app.get("/health")
async def health():
    return {"status": "ok"}
