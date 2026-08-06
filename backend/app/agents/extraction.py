"""Agent 5: Core extraction — action items, decisions, risks using GPT-4o."""
import time
import json
import hashlib
import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import (
    MeetingAgentState, ActionItem, Decision, Risk,
    StructuredReport, AuditEntry,
)
from app.config import settings
from app.prompts.extraction import EXTRACTION_SYSTEM_PROMPT

logger = structlog.get_logger()


def format_transcript_for_extraction(state: MeetingAgentState) -> str:
    """Format segments with speaker labels and timestamps."""
    speakers = {s.id: s.resolved_name or s.label for s in state.get("speakers", [])}
    lines = []
    for seg in state.get("transcript_segments", []):
        speaker = speakers.get(seg.speaker_id, seg.speaker_id)
        lines.append(f"[{seg.timestamp_label}] {speaker}: {seg.text}")
    return "\n".join(lines) if lines else state.get("transcript_raw", "")


def compute_fingerprint(owner: str, title: str, due_date: str) -> str:
    core = f"{owner.lower().strip()}::{title.lower().strip()}::{due_date.lower().strip()}"
    return hashlib.sha256(core.encode()).hexdigest()[:16]


async def extraction_node(state: MeetingAgentState) -> dict:
    """Extract all action items, decisions, risks from the transcript."""
    start = time.perf_counter()
    transcript = format_transcript_for_extraction(state)

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
        response_format={"type": "json_object"},
    )

    prompt = (
        f"Meeting Date: {state['meeting_date']}\n"
        f"Timezone: {state['timezone']}\n"
        f"Participants: {state.get('participants_hint', [])}\n\n"
        f"Transcript:\n{transcript[:12000]}"
    )

    try:
        response = await llm.ainvoke([
            SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        data = json.loads(response.content)
    except Exception as e:
        logger.error("Extraction LLM failed", error=str(e))
        return {
            "errors": [f"Extraction failed: {e}"],
            "action_items": [],
            "structured_report": StructuredReport(),
            "current_phase": "extraction_failed",
        }

    # Parse action items
    action_items = []
    for raw in data.get("action_items", []):
        try:
            fp = compute_fingerprint(
                raw.get("owner_raw", ""),
                raw.get("title", ""),
                raw.get("due_date_raw", ""),
            )
            item = ActionItem(
                title=raw.get("title", "Untitled"),
                description=raw.get("description", ""),
                owner_raw=raw.get("owner_raw", "UNKNOWN"),
                due_date_raw=raw.get("due_date_raw", ""),
                priority=raw.get("priority", "medium"),
                confidence=float(raw.get("confidence", 0.5)),
                evidence_timestamp=raw.get("evidence_timestamp", ""),
                evidence_quote=raw.get("evidence_quote", ""),
                meeting_section=raw.get("meeting_section", ""),
                dependencies=raw.get("dependencies", []),
                fingerprint=fp,
            )
            action_items.append(item)
        except Exception as e:
            logger.warning("Skipped malformed action item", error=str(e))

    # Parse decisions
    decisions = [
        Decision(
            description=d.get("description", ""),
            made_by=d.get("made_by", []),
            timestamp=d.get("timestamp", ""),
            confidence=float(d.get("confidence", 0.7)),
        )
        for d in data.get("decisions", [])
    ]

    # Parse risks
    risks = [
        Risk(
            description=r.get("description", ""),
            severity=r.get("severity", "medium"),
            owner=r.get("owner"),
        )
        for r in data.get("risks", [])
    ]

    report = StructuredReport(
        executive_summary=data.get("executive_summary", ""),
        decisions=decisions,
        open_questions=data.get("open_questions", []),
        risks=risks,
        dependencies=data.get("dependencies", []),
        discussion_topics=data.get("discussion_topics", []),
        key_insights=data.get("key_insights", []),
        follow_ups=data.get("follow_ups", []),
    )

    duration_ms = int((time.perf_counter() - start) * 1000)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="ExtractionAgent",
        action="extract_intelligence",
        output_summary=f"items={len(action_items)}, decisions={len(decisions)}, risks={len(risks)}",
        duration_ms=duration_ms,
    )

    return {
        "action_items": action_items,
        "structured_report": report,
        "current_phase": "extracted",
        "audit_log": [audit],
    }
