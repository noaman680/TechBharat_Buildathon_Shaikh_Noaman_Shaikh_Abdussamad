"""Build AuditEntry dicts from raw agent outputs."""
from datetime import datetime, timezone


def build_audit_entry(agent_name: str, result, reasoning: str = "", duration_ms: int = 0) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "action": "process",
        "input_summary": "",
        "output_summary": str(result)[:500],
        "reasoning": reasoning,
        "tool_calls": [],
        "duration_ms": duration_ms,
    }
