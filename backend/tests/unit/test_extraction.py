"""Unit tests for the extraction agent."""
import pytest
from unittest.mock import AsyncMock, patch
from app.agents.state import MeetingAgentState, TranscriptSegment, Speaker


def make_state(transcript: str, meeting_date: str = "2025-08-20") -> dict:
    return {
        "meeting_id": "test-meeting-001",
        "org_id": "test-org",
        "user_id": "test-user",
        "idempotency_key": "",
        "raw_input_path": "/tmp/test.txt",
        "input_type": "txt",
        "meeting_date": meeting_date,
        "timezone": "Asia/Kolkata",
        "participants_hint": ["alice@company.com", "bob@company.com"],
        "transcript_raw": transcript,
        "transcript_segments": [
            TranscriptSegment(
                speaker_id="SPEAKER_00", text=transcript,
                start_time=0.0, end_time=60.0, timestamp_label="00:00:00"
            )
        ],
        "speakers": [Speaker(id="SPEAKER_00", label="Alice")],
        "language_detected": "en",
        "planning_steps": [],
        "structured_report": None,
        "action_items": [],
        "verified_items": [],
        "pending_approval": [],
        "approved_items": [],
        "rejected_items": [],
        "approval_session_id": None,
        "execution_results": [],
        "current_phase": "planned",
        "errors": [],
        "warnings": [],
        "audit_log": [],
        "related_meetings": [],
        "recurring_owners": {},
        "overdue_followups": [],
    }


@pytest.mark.asyncio
async def test_extract_explicit_commitment():
    """A clear 'I will do X by Y' should extract with high confidence."""
    transcript = (
        "[00:05:30] Alice: I'll prepare the API documentation before next Friday.\n"
        "[00:05:35] Bob: Great, make sure to include the authentication section."
    )
    mock_response = {
        "executive_summary": "API documentation discussed.",
        "action_items": [{
            "title": "Prepare API documentation",
            "description": "Prepare full API documentation including authentication",
            "owner_raw": "Alice",
            "due_date_raw": "before next Friday",
            "priority": "high",
            "confidence": 0.92,
            "evidence_timestamp": "00:05:30",
            "evidence_quote": "I'll prepare the API documentation before next Friday.",
            "meeting_section": "discussion",
            "dependencies": [],
        }],
        "decisions": [],
        "open_questions": [],
        "risks": [],
        "dependencies": [],
        "discussion_topics": ["API documentation"],
        "key_insights": [],
        "follow_ups": [],
    }

    with patch("app.agents.extraction.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=AsyncMock(
            content=__import__("json").dumps(mock_response)
        ))
        mock_llm_cls.return_value = mock_llm

        from app.agents.extraction import extraction_node
        result = await extraction_node(make_state(transcript))

    items = result["action_items"]
    assert len(items) == 1
    assert items[0].owner_raw == "Alice"
    assert items[0].confidence >= 0.8
    assert "API documentation" in items[0].title
    assert "next Friday" in items[0].due_date_raw


@pytest.mark.asyncio
async def test_no_hallucination_on_vague_discussion():
    """Pure discussion without commitments should yield zero action items."""
    transcript = (
        "[00:01:00] Alice: We should probably think about the API design.\n"
        "[00:01:15] Bob: Yeah, it would be nice to have documentation.\n"
        "[00:01:30] Charlie: Agreed, maybe we can revisit that sometime."
    )
    mock_response = {
        "executive_summary": "General discussion about API design.",
        "action_items": [],
        "decisions": [],
        "open_questions": ["What should the API design look like?"],
        "risks": [],
        "dependencies": [],
        "discussion_topics": ["API design"],
        "key_insights": [],
        "follow_ups": ["Revisit API documentation"],
    }

    with patch("app.agents.extraction.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=AsyncMock(
            content=__import__("json").dumps(mock_response)
        ))
        mock_llm_cls.return_value = mock_llm

        from app.agents.extraction import extraction_node
        result = await extraction_node(make_state(transcript))

    assert len(result["action_items"]) == 0


@pytest.mark.asyncio
async def test_fingerprint_uniqueness():
    """Same task submitted twice should generate same fingerprint."""
    from app.agents.extraction import compute_fingerprint
    fp1 = compute_fingerprint("Alice", "Write API docs", "next Friday")
    fp2 = compute_fingerprint("Alice", "Write API docs", "next Friday")
    fp3 = compute_fingerprint("Bob", "Write API docs", "next Friday")
    assert fp1 == fp2
    assert fp1 != fp3


@pytest.mark.asyncio
async def test_multiple_action_items():
    """Multiple commitments in one transcript should all be extracted."""
    mock_response = {
        "executive_summary": "Sprint planning meeting.",
        "action_items": [
            {"title": "Fix login bug", "owner_raw": "Alice", "due_date_raw": "tomorrow",
             "priority": "critical", "confidence": 0.95,
             "evidence_timestamp": "00:02:10", "evidence_quote": "I'll fix the login bug tomorrow.",
             "description": "Fix authentication bug", "meeting_section": "bugs", "dependencies": []},
            {"title": "Update deployment pipeline", "owner_raw": "Bob", "due_date_raw": "end of week",
             "priority": "high", "confidence": 0.88,
             "evidence_timestamp": "00:08:45", "evidence_quote": "I can update the pipeline by Friday.",
             "description": "Update CI/CD pipeline", "meeting_section": "infra", "dependencies": []},
        ],
        "decisions": [{"description": "Move to microservices", "made_by": ["Alice", "Bob"],
                        "timestamp": "00:15:00", "confidence": 0.9}],
        "open_questions": [],
        "risks": [],
        "dependencies": [],
        "discussion_topics": ["bugs", "infrastructure"],
        "key_insights": ["Team will adopt microservices architecture"],
        "follow_ups": [],
    }

    with patch("app.agents.extraction.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=AsyncMock(
            content=__import__("json").dumps(mock_response)
        ))
        mock_llm_cls.return_value = mock_llm

        from app.agents.extraction import extraction_node
        result = await extraction_node(make_state("dummy transcript"))

    assert len(result["action_items"]) == 2
    assert result["structured_report"].decisions[0].description == "Move to microservices"
