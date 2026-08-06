"""
LangGraph workflow definition — wires the 12 agent nodes together with
conditional routing and a Postgres checkpointer for resumability.
See docs/BLUEPRINT.md §4 for the full design and §5 for each agent's spec.
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings
from app.agents.state import MeetingState
from app.agents.ingestion import ingestion_agent
from app.agents.transcription import transcription_agent
from app.agents.diarization import diarization_agent
from app.agents.planning import planning_agent
from app.agents.extraction import extraction_agent
from app.agents.verification import verification_agent
from app.agents.identity_resolution import identity_resolution_agent
from app.agents.calendar_resolution import calendar_resolution_agent
from app.agents.memory import memory_agent
from app.agents.approval import approval_agent
from app.agents.integration import integration_agent
from app.agents.audit import audit_agent, error_handler_node


def route_after_ingestion(state: MeetingState) -> str:
    if state.get("status") == "duplicate":
        return "duplicate"
    if state.get("errors"):
        return "error"
    if state["meeting_metadata"].get("needs_transcription", True):
        return "transcribe"
    return "already_text"


def route_after_verification(state: MeetingState) -> str:
    if state.get("errors"):
        return "error"
    if state.get("status") == "low_confidence":
        return "low_confidence"
    return "proceed"


def route_after_approval(state: MeetingState) -> str:
    if state.get("errors"):
        return "error"
    status = state.get("status")
    if status == "awaiting_approval":
        return "waiting"
    if state.get("approved_items") or state.get("edited_items"):
        return "approved"
    if state.get("rejected_items") and not state.get("approved_items"):
        return "rejected_all"
    return "waiting"


def build_meeting_graph() -> StateGraph:
    graph = StateGraph(MeetingState)

    # === NODES ===
    graph.add_node("ingestion", ingestion_agent)
    graph.add_node("transcription", transcription_agent)
    graph.add_node("diarization", diarization_agent)
    graph.add_node("planning", planning_agent)
    graph.add_node("extraction", extraction_agent)
    graph.add_node("verification", verification_agent)
    graph.add_node("identity_resolution", identity_resolution_agent)
    graph.add_node("calendar_resolution", calendar_resolution_agent)
    graph.add_node("memory_enrichment", memory_agent)
    graph.add_node("approval_gate", approval_agent)  # HITL node
    graph.add_node("integration", integration_agent)
    graph.add_node("audit_finalize", audit_agent)
    graph.add_node("error_handler", error_handler_node)

    # === EDGES ===
    graph.set_entry_point("ingestion")

    graph.add_conditional_edges("ingestion", route_after_ingestion, {
        "transcribe": "transcription",
        "already_text": "diarization",
        "duplicate": END,
        "error": "error_handler",
    })

    graph.add_edge("transcription", "diarization")
    graph.add_edge("diarization", "planning")
    graph.add_edge("planning", "extraction")
    graph.add_edge("extraction", "verification")

    graph.add_conditional_edges("verification", route_after_verification, {
        "proceed": "identity_resolution",
        "low_confidence": "extraction",  # Re-extract with more context
        "error": "error_handler",
    })

    graph.add_edge("identity_resolution", "calendar_resolution")
    graph.add_edge("calendar_resolution", "memory_enrichment")
    graph.add_edge("memory_enrichment", "approval_gate")

    # HITL — graph pauses here for human input
    graph.add_conditional_edges("approval_gate", route_after_approval, {
        "approved": "integration",
        "rejected_all": "audit_finalize",
        "waiting": "approval_gate",
        "error": "error_handler",
    })

    graph.add_edge("integration", "audit_finalize")
    graph.add_edge("audit_finalize", END)
    graph.add_edge("error_handler", END)

    # === CHECKPOINTING ===
    checkpointer = PostgresSaver.from_conn_string(settings.DATABASE_URL)
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["approval_gate"],
    )
