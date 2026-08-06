"""Agent 11: Integration — execute approved actions in external systems, safely."""
from app.agents.state import MeetingState
from app.db import db
from app.memory.redis_client import redis
from app.integrations.registry import IntegrationRegistry
from app.integrations.base import IntegrationError
import logging

logger = logging.getLogger(__name__)


async def integration_agent(state: MeetingState) -> MeetingState:
    """
    For each approved action item:
    1. Look up the user's configured integrations.
    2. Check the idempotency key before executing.
    3. Execute (payload preview already shown to the human before this runs).
    4. Record the API response.
    5. Handle failures gracefully — never partial-execute silently.
    """
    results = []
    approved = state["approved_items"] + state["edited_items"]

    for item in approved:
        idem_key = f"task:{state['meeting_id']}:{item['fingerprint']}"
        if await redis.exists(idem_key):
            results.append({"item_id": item["id"], "status": "skipped_duplicate"})
            continue

        integration_config = await db.integrations.get_for_org(
            state["organization_id"], item.get("preferred_integration")
        )

        try:
            result = await IntegrationRegistry.execute(item, integration_config)
            await redis.setex(idem_key, 86400 * 30, result["external_id"])
            results.append({"item_id": item["id"], "status": "success", **result})

        except IntegrationError as e:
            results.append({"item_id": item["id"], "status": "failed", "error": str(e)})
            logger.error("Integration failed for %s: %s", item["id"], e)

    return {**state, "execution_results": results}
