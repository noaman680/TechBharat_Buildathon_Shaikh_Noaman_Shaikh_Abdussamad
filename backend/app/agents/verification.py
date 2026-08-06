"""Agent 6: Verification — validate extractions, score confidence, reject hallucinations."""
from app.agents.state import MeetingState, ProcessingStatus
from app.services.verification import check_quote_exists, run_verification_llm


async def verification_agent(state: MeetingState) -> MeetingState:
    verified = []
    low_confidence_count = 0

    for item in state["action_items"]:
        # Check semantic similarity to verify the evidence quote actually exists
        similarity = await check_quote_exists(item["evidence_quote"], state["transcript_raw"])

        if similarity < 0.7:
            item["verified"] = False
            item["rejection_reason"] = "Evidence quote not found in transcript"
            item["confidence_score"] = 0.0
            continue

        # LLM-based verification for remaining items
        verification = await run_verification_llm(item, state["transcript_raw"])
        item.update(verification)

        if item["confidence_score"] < 0.5:
            low_confidence_count += 1

        verified.append(item)

    # If too many low-confidence items, re-extract with a different strategy
    if low_confidence_count / max(len(verified), 1) > 0.3:
        return {**state, "status": "low_confidence", "verified_items": verified}

    return {**state, "verified_items": verified, "status": ProcessingStatus.RESOLVING}
