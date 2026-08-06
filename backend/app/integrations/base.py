"""Base integration interface."""
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class IntegrationResult(BaseModel):
    success: bool
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    payload_sent: dict = {}
    response: dict = {}
    error: Optional[str] = None


class BaseIntegration(ABC):
    name: str

    @abstractmethod
    async def create_task(self, item, config: dict) -> IntegrationResult:
        """Create a task in the external system."""
        pass

    @abstractmethod
    async def check_existing(self, fingerprint: str, config: dict) -> Optional[str]:
        """Check if task already exists (idempotency). Returns external ID or None."""
        pass

    async def validate_credentials(self, config: dict) -> bool:
        return True
