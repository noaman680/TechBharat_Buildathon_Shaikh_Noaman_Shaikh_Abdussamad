"""
MeetingState — the single shared state object threaded through every
node of the LangGraph pipeline. See docs/BLUEPRINT.md §4 for design notes.
"""
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import add_messages
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    EXTRACTING = "extracting"
    VERIFYING = "verifying"
    RESOLVING = "resolving"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    COMPLETE = "complete"
    FAILED = "failed"


class SpeakerTurn(TypedDict):
    speaker_id: str
    speaker_name: Optional[str]
    start_time: float       # seconds from start
    end_time: float
    text: str
    confidence: float
    language: str


class ActionItem(TypedDict):
    id: str
    title: str
    description: str
    owner_raw: str                     # "Priya", "the dev team"
    owner_resolved: Optional[str]      # "Priya Shah"
    owner_email: Optional[str]         # "priya@company.com"
    due_date_raw: str                  # "next Friday"
    due_date_resolved: Optional[str]   # "2025-08-29"
    priority: str                      # high/medium/low
    confidence_score: float            # 0.0 - 1.0
    evidence_quote: str                # exact transcript text
    evidence_timestamp: float
    meeting_section: str
    dependencies: List[str]
    status: str                        # pending/approved/rejected/executed
    fingerprint: str                   # for deduplication


class MeetingReport(TypedDict):
    executive_summary: str
    decisions: List[dict]
    open_questions: List[dict]
    risks: List[dict]
    dependencies: List[dict]
    discussion_topics: List[dict]
    key_insights: List[dict]
    follow_ups: List[dict]


class AuditEntry(TypedDict):
    timestamp: str
    agent: str
    action: str
    input_summary: str
    output_summary: str
    reasoning: str
    tool_calls: List[dict]
    duration_ms: int


class MeetingState(TypedDict):
    # Identity
    meeting_id: str
    organization_id: str
    submitted_by: str

    # Input
    raw_input_path: str
    input_format: str       # txt/vtt/srt/mp3/mp4/wav
    input_hash: str         # SHA-256 for dedup

    # Processing
    status: ProcessingStatus
    transcript_raw: str
    transcript_turns: List[SpeakerTurn]
    meeting_metadata: dict  # date, timezone, participants, title

    # Intelligence
    analysis_plan: List[str]
    meeting_report: Optional[MeetingReport]
    action_items: List[ActionItem]
    verified_items: List[ActionItem]
    resolved_items: List[ActionItem]

    # Memory
    related_meeting_ids: List[str]
    historical_context: str
    carry_forward_items: List[ActionItem]

    # Approval
    approval_request_id: Optional[str]
    approved_items: List[ActionItem]
    rejected_items: List[ActionItem]
    edited_items: List[ActionItem]

    # Execution
    execution_results: List[dict]

    # Audit
    audit_trail: List[AuditEntry]
    errors: List[dict]

    # Agent messages (LangGraph native)
    messages: Annotated[list, add_messages]
