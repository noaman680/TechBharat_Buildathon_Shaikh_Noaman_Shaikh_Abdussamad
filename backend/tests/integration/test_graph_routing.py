"""Integration test placeholder for LangGraph conditional routing."""
import pytest

pytestmark = pytest.mark.skip(reason="TODO: needs a running Postgres checkpointer + mocked agents")


async def test_duplicate_meeting_routes_to_end():
    ...


async def test_low_confidence_reroutes_to_extraction():
    ...
