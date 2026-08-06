"""Asana integration."""
import httpx
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class AsanaIntegration(BaseIntegration):
    name = "asana"

    async def check_existing(self, fingerprint: str, config: dict) -> str | None:
        return None

    async def create_task(self, item, config: dict) -> IntegrationResult:
        token = config.get("access_token", settings.asana_access_token)
        workspace = config.get("workspace_gid", settings.asana_workspace_gid)

        if not token or not workspace:
            return IntegrationResult(success=False, error="Asana not configured.")

        owner = item.owner_resolved.resolved_name if item.owner_resolved else item.owner_raw
        notes = (
            f"{item.description}\n\n"
            f"Evidence [{item.evidence_timestamp}]: \"{item.evidence_quote}\"\n"
            f"Confidence: {item.confidence:.0%} | Priority: {item.priority}"
        )
        payload = {
            "data": {
                "name": item.title,
                "notes": notes,
                "workspace": workspace,
                "due_on": item.due_date_resolved,
                "tags": [],
            }
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://app.asana.com/api/1.0/tasks",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        if resp.status_code == 201:
            data = resp.json()["data"]
            return IntegrationResult(
                success=True, external_id=data["gid"],
                external_url=f"https://app.asana.com/0/{workspace}/{data['gid']}",
                payload_sent=payload, response={"gid": data["gid"]},
            )
        return IntegrationResult(success=False, error=f"Asana {resp.status_code}: {resp.text[:200]}")
