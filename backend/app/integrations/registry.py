"""Integration registry — manages all available integrations."""
from typing import Optional
from app.integrations.base import BaseIntegration


class IntegrationRegistry:
    _integrations: dict[str, type[BaseIntegration]] = {}

    def __init__(self):
        self._load_integrations()

    def _load_integrations(self):
        try:
            from app.integrations.jira import JiraIntegration
            self._integrations["jira"] = JiraIntegration
        except Exception:
            pass
        try:
            from app.integrations.github import GitHubIntegration
            self._integrations["github"] = GitHubIntegration
        except Exception:
            pass
        try:
            from app.integrations.slack import SlackIntegration
            self._integrations["slack"] = SlackIntegration
        except Exception:
            pass
        try:
            from app.integrations.notion import NotionIntegration
            self._integrations["notion"] = NotionIntegration
        except Exception:
            pass
        try:
            from app.integrations.asana import AsanaIntegration
            self._integrations["asana"] = AsanaIntegration
        except Exception:
            pass
        try:
            from app.integrations.google_calendar import GoogleCalendarIntegration
            self._integrations["google_calendar"] = GoogleCalendarIntegration
        except Exception:
            pass
        try:
            from app.integrations.linear import LinearIntegration
            self._integrations["linear"] = LinearIntegration
        except Exception:
            pass

    def get(self, name: str) -> Optional[BaseIntegration]:
        cls = self._integrations.get(name)
        return cls() if cls else None

    def list_available(self) -> list[str]:
        return list(self._integrations.keys())
