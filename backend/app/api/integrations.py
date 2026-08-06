"""
Integration configuration endpoints.

GET    /api/integrations                 -> List configured integrations
POST   /api/integrations                 -> Add new integration
POST   /api/integrations/{id}/test       -> Test connection
GET    /api/integrations/{id}/preview/{item_id} -> Preview exact outbound payload
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_integrations():
    raise NotImplementedError("TODO: list integrations for the current org")


@router.post("")
async def add_integration(config: dict):
    raise NotImplementedError("TODO: validate + store integration config (secrets in Vault)")


@router.post("/{integration_id}/test")
async def test_integration(integration_id: str):
    raise NotImplementedError("TODO: make a lightweight auth-check call to the external system")


@router.get("/{integration_id}/preview/{item_id}")
async def preview_payload(integration_id: str, item_id: str):
    """Show the exact API payload that would be sent — required before any execute."""
    raise NotImplementedError("TODO: build payload via IntegrationRegistry without sending it")
