"""Google Calendar integration — schedule follow-up meetings."""
import httpx
from datetime import datetime, timedelta
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class GoogleCalendarIntegration(BaseIntegration):
    name = "google_calendar"

    async def check_existing(self, fingerprint: str, config: dict) -> str | None:
        return None

    async def create_task(self, item, config: dict) -> IntegrationResult:
        """Schedule a follow-up calendar event for this action item."""
        access_token = config.get("access_token", "")
        calendar_id = config.get("calendar_id", "primary")

        if not access_token:
            return IntegrationResult(success=False, error="Google Calendar not configured (missing access_token).")

        due = item.due_date_resolved or (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")
        owner_email = item.owner_resolved.email if item.owner_resolved else None

        event = {
            "summary": f"[MeetMind] Due: {item.title}",
            "description": (
                f"Action item from meeting.\n\n"
                f"{item.description}\n\n"
                f"Evidence: \"{item.evidence_quote}\"\n"
                f"Confidence: {item.confidence:.0%}"
            ),
            "start": {"date": due},
            "end": {"date": due},
            "reminders": {"useDefault": False, "overrides": [{"method": "email", "minutes": 60 * 24}]},
        }

        if owner_email:
            event["attendees"] = [{"email": owner_email}]

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events",
                json=event,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if resp.status_code in (200, 201):
            data = resp.json()
            return IntegrationResult(success=True, external_id=data["id"],
                                     external_url=data.get("htmlLink"), response={"id": data["id"]})
        return IntegrationResult(success=False, error=f"Google Calendar {resp.status_code}: {resp.text[:200]}")
