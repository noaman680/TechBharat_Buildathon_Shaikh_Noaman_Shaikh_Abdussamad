"""Unit tests for calendar/date resolution."""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import date


@pytest.mark.asyncio
async def test_resolve_tomorrow():
    from app.agents.calendar_resolution import calendar_resolution_node
    from app.agents.state import ActionItem

    item = ActionItem(title="Test task", owner_raw="Alice", due_date_raw="tomorrow",
                       confidence=0.9, fingerprint="abc123")
    state = {
        "verified_items": [item],
        "meeting_date": "2025-08-20",
        "timezone": "UTC",
        "warnings": [],
        "audit_log": [],
    }
    result = await calendar_resolution_node(state)
    assert result["verified_items"][0].due_date_resolved == "2025-08-21"


@pytest.mark.asyncio
async def test_resolve_end_of_month():
    from app.agents.calendar_resolution import calendar_resolution_node
    from app.agents.state import ActionItem

    item = ActionItem(title="Month-end task", owner_raw="Bob", due_date_raw="end of month",
                       confidence=0.85, fingerprint="def456")
    state = {
        "verified_items": [item],
        "meeting_date": "2025-08-15",
        "timezone": "UTC",
        "warnings": [],
        "audit_log": [],
    }
    result = await calendar_resolution_node(state)
    resolved = result["verified_items"][0].due_date_resolved
    assert resolved is not None
    assert resolved.startswith("2025-08")


@pytest.mark.asyncio
async def test_no_date_skipped():
    from app.agents.calendar_resolution import calendar_resolution_node
    from app.agents.state import ActionItem

    item = ActionItem(title="No date task", owner_raw="Alice", due_date_raw="",
                       confidence=0.8, fingerprint="ghi789")
    state = {
        "verified_items": [item],
        "meeting_date": "2025-08-20",
        "timezone": "UTC",
        "warnings": [],
        "audit_log": [],
    }
    result = await calendar_resolution_node(state)
    assert result["verified_items"][0].due_date_resolved is None
