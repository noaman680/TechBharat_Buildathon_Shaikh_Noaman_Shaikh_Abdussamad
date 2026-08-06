"""Thin wrappers around the Anthropic client for the two models MeetMind uses."""
from anthropic import AsyncAnthropic

from app.config import settings

_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

# Primary reasoning model — planning, extraction, verification, RAG answers.
claude_client = _client

# Fast/cheap model — calendar resolution, quick classification.
claude_haiku_client = _client
