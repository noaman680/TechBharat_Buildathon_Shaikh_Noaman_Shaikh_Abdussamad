"""Fuzzy name matching against the org directory."""
from dataclasses import dataclass


@dataclass
class MatchResult:
    full_name: str
    email: str
    score: float


def fuzzy_match_person(owner_raw: str, org_directory: list) -> MatchResult | None:
    raise NotImplementedError("TODO: fuzzy match owner_raw against users.full_name/name_aliases")
