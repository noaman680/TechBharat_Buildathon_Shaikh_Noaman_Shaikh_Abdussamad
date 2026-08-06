"""Agent 7: Identity Resolution — resolve names to email addresses."""
import time
import json
import structlog
from thefuzz import process as fuzzy_process
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import MeetingAgentState, Speaker, AuditEntry
from app.config import settings

logger = structlog.get_logger()

IDENTITY_SYSTEM = """You are an identity resolution agent.
Given a name reference from a meeting and a list of known participants,
resolve the reference to the most likely participant.

Rules:
- Partial names: "Priya" → "Priya Shah"
- Role references: "the PM" → infer from context
- Pronoun chains: "she said she'd" → last female speaker
- If confidence < 0.7, set needs_manual_review: true

Output JSON: {"resolved_name": str, "email": str, "confidence": float,
              "reasoning": str, "needs_manual_review": bool}"""


async def resolve_single(name: str, participants: list[dict], transcript_context: str, llm) -> dict:
    prompt = (
        f"Name to resolve: \"{name}\"\n"
        f"Known participants: {json.dumps(participants)}\n"
        f"Transcript context (last 500 chars): {transcript_context[-500:]}"
    )
    response = await llm.ainvoke([
        SystemMessage(content=IDENTITY_SYSTEM),
        HumanMessage(content=prompt),
    ])
    return json.loads(response.content)


async def identity_resolution_node(state: MeetingAgentState) -> dict:
    """Resolve owner names in action items to actual identities."""
    start = time.perf_counter()
    items = state["verified_items"]
    participants_hint = state.get("participants_hint", [])
    recurring = state.get("recurring_owners", {})
    transcript = state.get("transcript_raw", "")

    # Build participant list from speakers + hints
    speakers = state.get("speakers", [])
    known_participants = []
    for s in speakers:
        if s.resolved_name:
            known_participants.append({"name": s.resolved_name, "email": s.email or ""})
    for email in participants_hint:
        parts = email.split("@")[0].replace(".", " ").title()
        known_participants.append({"name": parts, "email": email})

    llm = ChatOpenAI(model=settings.openai_fast_model, temperature=0,
                     response_format={"type": "json_object"})
    warnings = []

    for item in items:
        owner_key = item.owner_raw.lower().strip()

        # 1. Check historical memory
        if owner_key in recurring:
            cached = recurring[owner_key]
            item.owner_resolved = Speaker(
                label=item.owner_raw,
                resolved_name=cached.get("name"),
                email=cached.get("email"),
                confidence=0.95,
            )
            item.owner_confidence = 0.95
            continue

        # 2. Fuzzy match
        if known_participants:
            names = [p["name"] for p in known_participants]
            match, score = fuzzy_process.extractOne(item.owner_raw, names) or (None, 0)
            if match and score > 85:
                matched = next(p for p in known_participants if p["name"] == match)
                item.owner_resolved = Speaker(
                    label=item.owner_raw,
                    resolved_name=matched["name"],
                    email=matched.get("email"),
                    confidence=score / 100,
                )
                item.owner_confidence = score / 100
                continue

        # 3. LLM resolution
        if known_participants:
            try:
                result = await resolve_single(item.owner_raw, known_participants, transcript, llm)
                conf = float(result.get("confidence", 0.5))
                item.owner_resolved = Speaker(
                    label=item.owner_raw,
                    resolved_name=result.get("resolved_name", item.owner_raw),
                    email=result.get("email", ""),
                    confidence=conf,
                )
                item.owner_confidence = conf
                if result.get("needs_manual_review") or conf < 0.7:
                    warnings.append(
                        f"Low confidence owner: \'{item.owner_raw}\' ({conf:.0%}) — manual review needed"
                    )
            except Exception as e:
                warnings.append(f"Could not resolve owner \'{item.owner_raw}\': {e}")

    duration_ms = int((time.perf_counter() - start) * 1000)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="IdentityResolutionAgent",
        action="resolve_owners",
        output_summary=f"resolved={sum(1 for i in items if i.owner_resolved)}/{len(items)}",
        duration_ms=duration_ms,
    )

    return {
        "verified_items": items,
        "warnings": warnings,
        "current_phase": "identity_resolved",
        "audit_log": [audit],
    }
