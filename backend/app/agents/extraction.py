"""Agent 5: Extraction — pull decisions, tasks, risks, and questions out of the transcript."""
import hashlib

from app.agents.state import MeetingState
from app.clients.claude import claude_client
from app.prompts.extraction import EXTRACTION_PROMPT
from app.utils.transcript import format_transcript_for_extraction
from app.utils.parsing import parse_extraction_response


async def extraction_agent(state: MeetingState) -> MeetingState:
    formatted = format_transcript_for_extraction(state["transcript_turns"])

    response = await claude_client.messages.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(
            transcript=formatted,
            meeting_date=state["meeting_metadata"]["date"],
            participants=state["meeting_metadata"].get("participants", []),
            plan=state["analysis_plan"],
        )}],
        max_tokens=4000,
    )

    extracted = parse_extraction_response(response.content[0].text)

    # Assign fingerprints for deduplication
    for item in extracted["action_items"]:
        item["fingerprint"] = generate_fingerprint(item)

    return {
        **state,
        "action_items": extracted["action_items"],
        "meeting_report": {
            "executive_summary": extracted["summary"],
            "decisions": extracted["decisions"],
            "open_questions": extracted["open_questions"],
            "risks": extracted["risks"],
            "key_insights": extracted["key_insights"],
        },
    }


def generate_fingerprint(item: dict) -> str:
    """Semantic fingerprint for dedup — combines title + owner + due date."""
    key = f"{item['title'].lower()}|{item['owner_raw'].lower()}|{item['due_date_raw'].lower()}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]
