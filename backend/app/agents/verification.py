"""Agent 6: Verification — cross-check extracted items against transcript."""
import time
import json
import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import MeetingAgentState, AuditEntry
from app.config import settings
from app.prompts.verification import VERIFICATION_SYSTEM_PROMPT

logger = structlog.get_logger()


async def verification_node(state: MeetingAgentState) -> dict:
    """Verify each extracted action item is genuinely supported by the transcript."""
    start = time.perf_counter()
    items = state["action_items"]
    transcript = state.get("transcript_raw", "")[:8000]

    if not items:
        return {"verified_items": [], "current_phase": "verified", "audit_log": []}

    llm = ChatOpenAI(model=settings.openai_model, temperature=0,
                     response_format={"type": "json_object"})

    items_json = json.dumps([{
        "id": item.id,
        "title": item.title,
        "owner_raw": item.owner_raw,
        "evidence_quote": item.evidence_quote,
        "confidence": item.confidence,
    } for item in items])

    try:
        response = await llm.ainvoke([
            SystemMessage(content=VERIFICATION_SYSTEM_PROMPT),
            HumanMessage(content=f"Transcript:\n{transcript}\n\nItems to verify:\n{items_json}"),
        ])
        verification = json.loads(response.content)
    except Exception as e:
        logger.warning("Verification LLM failed, passing all items", error=str(e))
        return {
            "verified_items": items,
            "current_phase": "verified",
            "warnings": [f"Verification skipped: {e}"],
        }

    verified_map = {v["id"]: v for v in verification.get("results", [])}
    verified_items = []
    warnings = []

    for item in items:
        result = verified_map.get(item.id, {})
        is_verified = result.get("verified", True)
        adjusted_conf = float(result.get("adjusted_confidence", item.confidence))

        if is_verified and adjusted_conf >= 0.6:
            item.confidence = adjusted_conf
            verified_items.append(item)
        else:
            reason = result.get("rejection_reason", "Low confidence")
            warnings.append(f"Rejected: '{item.title}' — {reason}")

    duration_ms = int((time.perf_counter() - start) * 1000)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="VerificationAgent",
        action="cross_verify_items",
        output_summary=f"verified={len(verified_items)}/{len(items)}, rejected={len(items)-len(verified_items)}",
        duration_ms=duration_ms,
    )

    return {
        "verified_items": verified_items,
        "current_phase": "verified",
        "warnings": warnings,
        "audit_log": [audit],
    }
