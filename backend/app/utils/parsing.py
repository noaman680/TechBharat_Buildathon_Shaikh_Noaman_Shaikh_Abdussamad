"""Parse JSON responses returned by Claude for each agent."""
import json


def parse_plan(raw_text: str) -> list:
    return json.loads(raw_text)


def parse_extraction_response(raw_text: str) -> dict:
    return json.loads(raw_text)
