"""Agent 4: Planning — decompose the meeting into an analysis plan (ReAct-style)."""
from app.agents.state import MeetingState
from app.clients.claude import claude_client
from app.prompts.planning import PLANNING_PROMPT
from app.utils.parsing import parse_plan


async def planning_agent(state: MeetingState) -> MeetingState:
    plan = await claude_client.messages.create(
        model="claude-sonnet-4-6",
        messages=[{
            "role": "user",
            "content": f"{PLANNING_PROMPT}\n\nTranscript:\n{state['transcript_raw'][:50000]}",
        }],
        max_tokens=1000,
    )
    return {**state, "analysis_plan": parse_plan(plan.content[0].text)}
