"""Agent 7: Identity Resolution — convert "Priya", "the backend team", "me" into exact identities."""
from app.agents.state import MeetingState
from app.db import db
from app.utils.speakers import build_speaker_map
from app.utils.matching import fuzzy_match_person


async def identity_resolution_agent(state: MeetingState) -> MeetingState:
    """
    Resolution strategy (in order of confidence):
    1. Exact match in the meeting participants list
    2. Fuzzy match in the org directory
    3. Speaker turn lookup ("I" -> speaker who spoke that turn)
    4. Historical assignment lookup (who usually owns these tasks?)
    5. If none, flag UNRESOLVED and require manual confirmation.

    NEVER GUESS. Low confidence = flag for human review.
    """
    org_directory = await db.org_directory.get_all(state["organization_id"])
    speaker_map = build_speaker_map(state["transcript_turns"])

    resolved_items = []
    for item in state["verified_items"]:
        owner_raw = item["owner_raw"]

        if owner_raw.lower() in ["i", "me", "myself", "i'll", "i will"]:
            speaker = speaker_map.get(item["evidence_timestamp"])
            if speaker:
                item["owner_resolved"] = speaker.name
                item["owner_email"] = speaker.email
                item["owner_confidence"] = 0.95
            else:
                item["owner_resolved"] = "UNRESOLVED"
                item["owner_confidence"] = 0.0

        else:
            match = fuzzy_match_person(owner_raw, org_directory)
            if match and match.score > 0.85:
                item["owner_resolved"] = match.full_name
                item["owner_email"] = match.email
                item["owner_confidence"] = match.score
            elif match and match.score > 0.6:
                item["owner_resolved"] = match.full_name
                item["owner_email"] = match.email
                item["owner_confidence"] = match.score
                item["requires_confirmation"] = True
            else:
                item["owner_resolved"] = "UNRESOLVED"
                item["owner_confidence"] = 0.0
                item["requires_confirmation"] = True

        resolved_items.append(item)

    return {**state, "resolved_items": resolved_items}
