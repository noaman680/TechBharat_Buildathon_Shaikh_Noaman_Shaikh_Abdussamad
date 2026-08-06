"""Notion integration."""
import httpx
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class NotionIntegration(BaseIntegration):
    name = "notion"

    async def check_existing(self, fingerprint: str, config: dict) -> str | None:
        return None

    async def create_task(self, item, config: dict) -> IntegrationResult:
        token = config.get("api_key", settings.notion_api_key)
        db_id = config.get("database_id", settings.notion_database_id)

        if not token or not db_id:
            return IntegrationResult(success=False, error="Notion not configured.")

        owner = item.owner_resolved.resolved_name if item.owner_resolved else item.owner_raw
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "Name": {"title": [{"text": {"content": item.title}}]},
                "Owner": {"rich_text": [{"text": {"content": owner}}]},
                "Priority": {"select": {"name": item.priority.capitalize()}},
                "Status": {"select": {"name": "Not started"}},
                "Due Date": {"date": {"start": item.due_date_resolved}} if item.due_date_resolved else {"date": None},
                "Confidence": {"number": round(item.confidence * 100)},
                "Evidence": {"rich_text": [{"text": {"content": item.evidence_quote[:200]}}]},
            },
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.notion.com/v1/pages",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json",
                },
            )

        if resp.status_code == 200:
            data = resp.json()
            return IntegrationResult(success=True, external_id=data["id"],
                                     external_url=data.get("url"),
                                     payload_sent=payload, response={"id": data["id"]})
        return IntegrationResult(success=False, error=f"Notion API {resp.status_code}: {resp.text[:200]}")
