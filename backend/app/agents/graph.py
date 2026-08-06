"""LangGraph graph builder for MeetMind multi-agent pipeline."""
from langgraph.graph import StateGraph, END
from langgraph.types import Command

from app.agents.state import MeetingAgentState
from app.agents.ingestion import ingestion_node
from app.agents.transcription import transcription_node
from app.agents.diarization import diarization_node
from app.agents.planning import planning_node
from app.agents.extraction import extraction_node
from app.agents.verification import verification_node
from app.agents.identity_resolution import identity_resolution_node
from app.agents.calendar_resolution import calendar_resolution_node
from app.agents.memory import memory_node
from app.agents.approval import approval_node
from app.agents.integration import integration_node
from app.agents.audit import audit_node


def route_after_ingestion(state: MeetingAgentState) -> str:
    if state["errors"]:
        return "audit"
    if state["input_type"] in ("audio", "video"):
        return "transcribe"
    return "plan"


def route_after_verification(state: MeetingAgentState) -> str:
    low_confidence = [i for i in state["verified_items"] if i.confidence < 0.6]
    if len(low_confidence) > len(state["verified_items"]) * 0.5:
        return "re_extract"
    return "resolve_identity"


def route_after_approval(state: MeetingAgentState) -> str:
    if not state["approved_items"]:
        return "audit"
    return "execute"


def build_graph(checkpointer=None) -> StateGraph:
    g = StateGraph(MeetingAgentState)

    # Register nodes
    g.add_node("ingest",            ingestion_node)
    g.add_node("transcribe",        transcription_node)
    g.add_node("diarize",           diarization_node)
    g.add_node("plan",              planning_node)
    g.add_node("extract",           extraction_node)
    g.add_node("verify",            verification_node)
    g.add_node("resolve_identity",  identity_resolution_node)
    g.add_node("resolve_dates",     calendar_resolution_node)
    g.add_node("memory",            memory_node)
    g.add_node("await_approval",    approval_node)
    g.add_node("execute",           integration_node)
    g.add_node("audit",             audit_node)

    # Entry point
    g.set_entry_point("ingest")

    # Edges
    g.add_conditional_edges("ingest", route_after_ingestion, {
        "transcribe": "transcribe",
        "plan": "plan",
        "audit": "audit",
    })

    g.add_edge("transcribe", "diarize")
    g.add_edge("diarize", "plan")
    g.add_edge("plan", "extract")

    g.add_conditional_edges("verify", route_after_verification, {
        "re_extract": "extract",
        "resolve_identity": "resolve_identity",
    })

    g.add_edge("extract", "verify")
    g.add_edge("resolve_identity", "resolve_dates")
    g.add_edge("resolve_dates", "memory")
    g.add_edge("memory", "await_approval")

    # HUMAN-IN-THE-LOOP checkpoint: execution pauses here
    g.add_conditional_edges("await_approval", route_after_approval, {
        "execute": "execute",
        "audit": "audit",
    })

    g.add_edge("execute", "audit")
    g.add_edge("audit", END)

    kwargs = {}
    if checkpointer:
        kwargs["checkpointer"] = checkpointer
        kwargs["interrupt_before"] = ["await_approval"]

    return g.compile(**kwargs)
