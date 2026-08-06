"""Jira integration."""
import httpx
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings

PRIORITY_MAP = {"critical": "Highest", "high": "High", "medium": "Medium", "low": "Low"}


class JiraIntegration(BaseIntegration):
    name = "jira"

    async def check_existing(self, fingerprint: str, config: dict) -> str | None:
        base_url = config.get("base_url", settings.jira_base_url)
        token = config.get("api_token", settings.jira_api_token)
        email = config.get("email", settings.jira_email)
        project = config.get("project_key", settings.jira_project_key)

        jql = f'project={project} AND labels="meetmind-{fingerprint}"' 
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{base_url}/rest/api/3/search",
                params={"jql": jql, "maxResults": 1},
                auth=(email, token),
            )
            if resp.status_code == 200:
                issues = resp.json().get("issues", [])
                if issues:
                    return issues[0]["key"]
        return None

    async def create_task(self, item, config: dict) -> IntegrationResult:
        base_url = config.get("base_url", settings.jira_base_url)
        token = config.get("api_token", settings.jira_api_token)
        email = config.get("email", settings.jira_email)
        project = config.get("project_key", settings.jira_project_key)

        if not all([base_url, token, email]):
            return IntegrationResult(
                success=False,
                error="Jira not configured. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN.",
            )

        # Idempotency check
        existing = await self.check_existing(item.fingerprint, config)
        if existing:
            return IntegrationResult(
                success=True,
                external_id=existing,
                external_url=f"{base_url}/browse/{existing}",
                error="Duplicate — returned existing issue",
            )

        owner_email = None
        if item.owner_resolved:
            owner_email = item.owner_resolved.email

        payload = {
            "fields": {
                "project": {"key": project},
                "summary": item.title,
                "description": {
                    "version": 1,
                    "type": "doc",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": (
                            f"{item.description}\n\n"
                            f"Evidence [{item.evidence_timestamp}]: \"{item.evidence_quote}\""
                        )}],
                    }],
                },
                "issuetype": {"name": "Task"},
                "priority": {"name": PRIORITY_MAP.get(item.priority, "Medium")},
                "labels": [
                    "meetmind",
                    f"meetmind-{item.fingerprint}",
                    f"meeting-{item.meeting_id[:8] if hasattr(item, 'meeting_id') else 'unknown'}",
                ],
            }
        }

        if item.due_date_resolved:
            payload["fields"]["duedate"] = item.due_date_resolved

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/rest/api/3/issue",
                json=payload,
                auth=(email, token),
                timeout=30,
            )

        if resp.status_code in (200, 201):
            data = resp.json()
            return IntegrationResult(
                success=True,
                external_id=data["key"],
                external_url=f"{base_url}/browse/{data['key']}",
                payload_sent=payload,
                response=data,
            )
        else:
            return IntegrationResult(
                success=False,
                payload_sent=payload,
                response=resp.json(),
                error=f"Jira API error {resp.status_code}: {resp.text[:200]}",
            )
