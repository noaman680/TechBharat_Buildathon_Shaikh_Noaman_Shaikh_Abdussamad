"""LangGraph state definition for the MeetMind agent pipeline."""
from __future__ import annotations
import operator
from typing import TypedDict, Annotated, Optional, Literal, Any
from pydantic import BaseModel, Field
import uuid


class Speaker(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: str
    resolved_name: Optional[str] = None
    email: Optional[str] = None
    confidence: float = 0.0


class TranscriptSegment(BaseModel):
    speaker_id: str
    text: str
    start_time: float
    end_time: float
    timestamp_label: str


class ActionItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str = ""
    owner_raw: str
    owner_resolved: Optional[Speaker] = None
    owner_confidence: float = 0.0
    due_date_raw: str = ""
    due_date_resolved: Optional[str] = None
    priority: Literal["critical", "high", "medium", "low"] = "medium"
    confidence: float = 0.0
    evidence_timestamp: str = ""
    evidence_quote: str = ""
    meeting_section: str = ""
    dependencies: list[str] = Field(default_factory=list)
    fingerprint: str = ""
    status: Literal["pending", "approved", "rejected", "executed"] = "pending"
    target_integration: str = "jira"
    external_ref: Optional[dict] = None


class Decision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    made_by: list[str] = Field(default_factory=list)
    timestamp: str = ""
    confidence: float = 0.0


class Risk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    severity: Literal["critical", "high", "medium", "low"] = "medium"
    owner: Optional[str] = None


class StructuredReport(BaseModel):
    executive_summary: str = ""
    decisions: list[Decision] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    discussion_topics: list[str] = Field(default_factory=list)
    key_insights: list[str] = Field(default_factory=list)
    follow_ups: list[str] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    action_item_id: str
    integration: str
    status: Literal["success", "failed", "skipped"]
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    request_payload: Optional[dict] = None
    response_payload: Optional[dict] = None
    error: Optional[str] = None


class AuditEntry(BaseModel):
    timestamp: str
    agent: str
    action: str
    input_summary: str = ""
    output_summary: str = ""
    reasoning: Optional[str] = None
    tool_calls: list[dict] = Field(default_factory=list)
    duration_ms: int = 0


class MeetingAgentState(TypedDict):
    """Full state carried through the LangGraph agent pipeline."""
    meeting_id: str
    org_id: str
    user_id: str
    idempotency_key: str
    raw_input_path: str
    input_type: Literal["txt", "vtt", "srt", "audio", "video"]
    meeting_date: str
    timezone: str
    participants_hint: list[str]
    transcript_raw: Optional[str]
    transcript_segments: list[TranscriptSegment]
    speakers: list[Speaker]
    language_detected: str
    planning_steps: list[str]
    structured_report: Optional[StructuredReport]
    action_items: list[ActionItem]
    verified_items: list[ActionItem]
    pending_approval: list[ActionItem]
    approved_items: list[ActionItem]
    rejected_items: list[ActionItem]
    approval_session_id: Optional[str]
    execution_results: list[ExecutionResult]
    current_phase: str
    errors: Annotated[list[str], operator.add]
    warnings: Annotated[list[str], operator.add]
    audit_log: Annotated[list[AuditEntry], operator.add]
    related_meetings: list[str]
    recurring_owners: dict[str, Any]
    overdue_followups: list[dict]
