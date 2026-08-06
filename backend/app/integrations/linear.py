"""Linear integration."""
import httpx
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings

PRIORITY_MAP = {"critical": 1, "high": 2, "medium": 3, "low": 4}


class LinearIntegration(BaseIntegration):
    name = "linear"

    async def check_existing(self, fingerprint: str, config: dict) -> str | None:
        return None

    async def create_task(self, item, config: dict) -> IntegrationResult:
        token = config.get("api_key", getattr(settings, "linear_api_key", ""))
        team_id = config.get("team_id", getattr(settings, "linear_team_id", ""))

        if not token or not team_id:
            return IntegrationResult(success=False, error="Linear not configured.")

        query = """
        mutation IssueCreate($input: IssueCreateInput!) {
          issueCreate(input: $input) { success issue { id url identifier } }
        }
        """
        variables = {
            "input": {
                "title": item.title,
                "description": f"{item.description}\n\nEvidence: \"{item.evidence_quote}\" [{item.evidence_timestamp}]",
                "teamId": team_id,
                "priority": PRIORITY_MAP.get(item.priority, 3),
                "dueDate": item.due_date_resolved,
            }
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.linear.app/graphql",
                json={"query": query, "variables": variables},
                headers={"Authorization": token, "Content-Type": "application/json"},
            )

        if resp.status_code == 200:
            data = resp.json().get("data", {}).get("issueCreate", {})
            if data.get("success"):
                issue = data["issue"]
                return IntegrationResult(success=True, external_id=issue["id"],
                                         external_url=issue["url"],
                                         response={"id": issue["id"], "identifier": issue["identifier"]})
        return IntegrationResult(success=False, error=f"Linear error: {resp.text[:200]}")
