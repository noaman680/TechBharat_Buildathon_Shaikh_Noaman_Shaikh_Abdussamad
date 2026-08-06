"""Integration management routes."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class IntegrationConfig(BaseModel):
    integration: str
    config: dict


@router.get("/available")
async def list_integrations():
    """List all supported integrations."""
    from app.integrations.registry import IntegrationRegistry
    registry = IntegrationRegistry()
    return {"integrations": registry.list_available()}


@router.post("/test")
async def test_integration(body: IntegrationConfig):
    """Test integration credentials."""
    from app.integrations.registry import IntegrationRegistry
    registry = IntegrationRegistry()
    integration = registry.get(body.integration)
    if not integration:
        return {"success": False, "error": f"Integration '{body.integration}' not found"}
    valid = await integration.validate_credentials(body.config)
    return {"success": valid, "integration": body.integration}
