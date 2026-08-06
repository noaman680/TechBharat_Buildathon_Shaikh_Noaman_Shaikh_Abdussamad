"""Code-switched language handling (Hindi/English etc). See docs/BLUEPRINT.md Appendix B."""

TECHNICAL_TERMS = ["API", "PR", "sprint", "backend", "frontend", "deploy", "merge", "commit"]


async def handle_code_switched_transcript(whisper_result: dict) -> dict:
    """
    Detect non-English segments and translate them while preserving technical
    terms, so extraction always runs against consistent English text.
    """
    raise NotImplementedError(
        "TODO: for each non-English segment, call translate_with_term_preservation() "
        "and attach segment.text_translated / segment.text_original"
    )


async def translate_with_term_preservation(text: str, source_lang: str,
                                            preserve_terms: list, target_lang: str) -> str:
    raise NotImplementedError("TODO: translate via LLM call, keeping preserve_terms verbatim")
