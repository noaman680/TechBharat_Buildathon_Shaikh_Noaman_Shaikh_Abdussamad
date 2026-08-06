"""Shared pytest fixtures."""
import pytest


@pytest.fixture
def sample_action_item():
    return {
        "id": "item-1",
        "title": "Prepare API documentation",
        "description": "Write and publish the API docs the team is blocked on.",
        "owner_raw": "Priya",
        "owner_resolved": None,
        "owner_email": None,
        "due_date_raw": "next Friday",
        "due_date_resolved": None,
        "priority": "high",
        "confidence_score": 0.96,
        "evidence_quote": "I'll finish the documentation before next Friday",
        "evidence_timestamp": 1937.2,
        "meeting_section": "Sprint Planning",
        "dependencies": [],
        "status": "pending",
        "fingerprint": "",
    }
