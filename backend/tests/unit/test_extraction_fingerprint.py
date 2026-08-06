"""Unit test for the deterministic fingerprint used for dedup."""
from app.agents.extraction import generate_fingerprint


def test_fingerprint_is_deterministic():
    item = {"title": "Prepare API docs", "owner_raw": "Priya", "due_date_raw": "next Friday"}
    assert generate_fingerprint(item) == generate_fingerprint(item)


def test_fingerprint_is_case_insensitive():
    a = {"title": "Prepare API Docs", "owner_raw": "priya", "due_date_raw": "Next Friday"}
    b = {"title": "prepare api docs", "owner_raw": "Priya", "due_date_raw": "next friday"}
    assert generate_fingerprint(a) == generate_fingerprint(b)
