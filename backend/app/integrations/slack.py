from app.agents.state import MeetingReport
from app.integrations.base import BaseIntegration
from app.integrations.registry import IntegrationRegistry


@IntegrationRegistry.register("slack")
class SlackIntegration(BaseIntegration):
    async def create_task(self, item):
        # Slack is used for recap posting rather than task creation.
        raise NotImplementedError("Use post_recap() for Slack")

    async def post_recap(self, report: MeetingReport, meeting) -> dict:
        blocks = self._build_recap_blocks(report, meeting)
        response = await self.client.post("/chat.postMessage", json={
            "channel": self.config["channel_id"],
            "blocks": blocks,
            "text": f"Meeting Recap: {meeting.title}",
        })
        return {"external_id": response["ts"], "external_url": response["permalink"]}

    def _build_recap_blocks(self, report: MeetingReport, meeting) -> list:
        raise NotImplementedError("TODO: build Slack Block Kit blocks from the report")

    @property
    def client(self):
        raise NotImplementedError("TODO: wire up an authenticated Slack HTTP client")
