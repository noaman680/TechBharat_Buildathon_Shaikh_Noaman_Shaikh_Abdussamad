"""Quote-existence check and LLM-based verification for the verification agent."""


async def check_quote_exists(evidence_quote: str, transcript_raw: str) -> float:
    """Return a 0-1 similarity score for whether the quote genuinely appears in the transcript."""
    raise NotImplementedError("TODO: fuzzy/substring match evidence_quote against transcript_raw")


async def run_verification_llm(item: dict, transcript_raw: str) -> dict:
    raise NotImplementedError(
        "TODO: call Claude with VERIFICATION_PROMPT, return verified/confidence_score/"
        "rejection_reason/confidence_explanation"
    )
