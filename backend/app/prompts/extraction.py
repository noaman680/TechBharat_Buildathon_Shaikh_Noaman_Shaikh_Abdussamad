EXTRACTION_PROMPT = """
You are an expert Meeting Intelligence Extractor.

Analyze this meeting transcript and extract ALL of the following:

## ACTION ITEMS
For each commitment, extract:
- title: Short imperative phrase
- description: What needs to be done and why
- owner_raw: Exact name/reference as spoken ("Priya", "the backend team", "I")
- due_date_raw: Exact phrase as spoken ("next Friday", "before the sprint ends", "ASAP")
- priority: high/medium/low — infer from context, urgency words, speaker emphasis
- confidence_score: 0.0-1.0 — how certain are you this is a real commitment?
- evidence_quote: The EXACT transcript sentence(s) that establish this commitment
- evidence_timestamp: Start time (seconds) of the evidence
- meeting_section: Which part of the meeting this came from
- dependencies: IDs of other action items this blocks on

## DECISIONS
Finalized, non-reversible decisions made during the meeting.

## OPEN QUESTIONS
Questions raised but not resolved.

## RISKS
Potential blockers or concerns explicitly or implicitly mentioned.

## KEY INSIGHTS
Important discoveries, metrics, or revelations.

CRITICAL RULES:
1. NEVER invent action items not present in the transcript
2. If ownership is ambiguous, set owner_raw to "UNRESOLVED" with confidence < 0.5
3. Only extract COMMITMENTS — not suggestions, hypotheticals, or past work
4. Use marker phrases: "I will", "we'll", "can you", "let's make sure", "I'll take", "I'll handle"
5. Disagreement Detection: Flag unresolved disagreements as OPEN QUESTIONS

Transcript with speaker turns:
{transcript}

Meeting date: {meeting_date}
Participants: {participants}
Analysis plan: {plan}

Return ONLY valid JSON. No preamble.
"""

# Few-shot examples to splice into the prompt above when calibrating the model.
POSITIVE_EXAMPLE = """
Speaker: Priya Shah (00:32:17)
"I'll finish the documentation before next Friday — I know the team is blocked on it."

-> {"title": "Prepare API documentation", "owner_raw": "Priya", "due_date_raw": "next Friday",
    "confidence": 0.96, "evidence_quote": "I'll finish the documentation before next Friday"}
"""

NEGATIVE_EXAMPLE = """
Speaker: Rahul Kumar (00:45:02)
"We should probably look into improving the deployment pipeline at some point."

-> NOT an action item — "should probably" + "at some point" = suggestion, not commitment
"""
