"""Base class every external-system integration implements."""
from abc import ABC, abstractmethod

from app.agents.state import ActionItem


class IntegrationError(Exception):
    """Raised when an external system call fails in a handled way."""


class BaseIntegration(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    async def create_task(self, item: ActionItem) -> dict:
        """Create a task/issue in the external system. Returns external_id + external_url."""
        raise NotImplementedError
