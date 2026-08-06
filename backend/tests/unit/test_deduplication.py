"""Unit tests for deduplication logic."""
import pytest
from unittest.mock import AsyncMock, patch
from app.agents.state import ActionItem


@pytest.mark.asyncio
async def test_duplicate_fingerprint_blocked():
    """Same fingerprint should be blocked."""
    from app.agents.extraction import compute_fingerprint
    from app.agents.memory import memory_node

    fp = compute_fingerprint("alice", "Write API docs", "next friday")

    with patch("app.agents.memory.MemoryService") as MockMemory:
        mock_svc = AsyncMock()
        mock_svc.is_duplicate.return_value = (True, "Write API docs")
        mock_svc.get_overdue_tasks.return_value = []
        mock_svc.find_related_meetings.return_value = []
        mock_svc.get_recurring_owners.return_value = {}
        MockMemory.return_value = mock_svc

        item = ActionItem(title="Write API docs", owner_raw="Alice",
                           confidence=0.9, fingerprint=fp)
        state = {
            "verified_items": [item],
            "org_id": "test-org",
            "structured_report": None,
            "warnings": [],
            "audit_log": [],
            "participants_hint": [],
            "speakers": [],
        }
        result = await memory_node(state)

    assert len(result["verified_items"]) == 0
    assert any("duplicate" in w.lower() for w in result["warnings"])


@pytest.mark.asyncio
async def test_unique_item_passes():
    """Unique item should pass deduplication."""
    with patch("app.agents.memory.MemoryService") as MockMemory:
        mock_svc = AsyncMock()
        mock_svc.is_duplicate.return_value = (False, None)
        mock_svc.get_overdue_tasks.return_value = []
        mock_svc.find_related_meetings.return_value = []
        mock_svc.get_recurring_owners.return_value = {}
        MockMemory.return_value = mock_svc

        item = ActionItem(title="Brand new unique task", owner_raw="Bob",
                           confidence=0.85, fingerprint="unique-fp")
        state = {
            "verified_items": [item],
            "org_id": "test-org",
            "structured_report": None,
            "warnings": [],
            "audit_log": [],
            "participants_hint": [],
            "speakers": [],
        }
        result = await memory_node(state)

    assert len(result["verified_items"]) == 1
