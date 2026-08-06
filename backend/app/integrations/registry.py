"""Plugin-based integration system — easy to add new external tools."""
from typing import Dict

from app.agents.state import ActionItem
from app.integrations.base import BaseIntegration, IntegrationError


class IntegrationRegistry:
    _integrations: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(integration_class):
            cls._integrations[name] = integration_class
            return integration_class
        return decorator

    @classmethod
    async def execute(cls, item: ActionItem, config: dict) -> dict:
        system = config["system_type"]
        integration = cls._integrations.get(system)
        if not integration:
            raise IntegrationError(f"No integration registered for {system}")
        return await integration(config).create_task(item)
