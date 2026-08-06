"""Slack integration — post meeting recaps."""
import httpx
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class SlackIntegration(BaseIntegration):
    name = "slack"

    async def check_existing(self, fingerprint: str, config: dict) -> str | None:
        return None  # Slack messages are not deduplicated

    async def create_task(self, item, config: dict) -> IntegrationResult:
        """Post action item as a Slack message."""
        token = config.get("bot_token", settings.slack_bot_token)
        channel = config.get("channel_id", settings.slack_channel_id)

        if not token or not channel:
            return IntegrationResult(success=False, error="Slack not configured.")

        owner = item.owner_resolved.resolved_name if item.owner_resolved else item.owner_raw
        due = item.due_date_resolved or item.due_date_raw or "TBD"
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(item.priority, "⚪")

        blocks = [
            {"type": "section", "text": {"type": "mrkdwn",
                "text": f"{emoji} *Action Item:* {item.title}"}},
            {"type": "section", "fields": [
                {"type": "mrkdwn", "text": f"*Owner:* {owner}"},
                {"type": "mrkdwn", "text": f"*Due:* {due}"},
                {"type": "mrkdwn", "text": f"*Priority:* {item.priority.capitalize()}"},
                {"type": "mrkdwn", "text": f"*Confidence:* {item.confidence:.0%}"},
            ]},
            {"type": "context", "elements": [
                {"type": "mrkdwn", "text": f"💬 _{item.evidence_quote}_ [{item.evidence_timestamp}]"}
            ]},
        ]

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://slack.com/api/chat.postMessage",
                json={"channel": channel, "blocks": blocks,
                      "text": f"Action Item: {item.title} (Owner: {owner})"},
                headers={"Authorization": f"Bearer {token}"},
            )

        data = resp.json()
        if data.get("ok"):
            return IntegrationResult(success=True, external_id=data.get("ts"),
                                     response={"ts": data.get("ts"), "channel": data.get("channel")})
        return IntegrationResult(success=False, error=data.get("error", "Unknown Slack error"))

    async def post_meeting_recap(self, report, items: list, config: dict) -> IntegrationResult:
        """Post full meeting recap to Slack channel."""
        token = config.get("bot_token", settings.slack_bot_token)
        channel = config.get("channel_id", settings.slack_channel_id)

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "📋 MeetMind — Meeting Intelligence Report"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Summary:*\n{report.executive_summary}"}},
            {"type": "divider"},
        ]

        if report.decisions:
            decision_text = "\n".join(f"• {d.description}" for d in report.decisions[:5])
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"*✅ Decisions:*\n{decision_text}"}})

        if items:
            item_text = "\n".join(
                f"• *{i.title}* — {i.owner_resolved.resolved_name if i.owner_resolved else i.owner_raw} by {i.due_date_resolved or 'TBD'}"
                for i in items[:8]
            )
            blocks.append({"type": "section", "text": {"type": "mrkdwn",
                "text": f"*🎯 Action Items ({len(items)}):*\n{item_text}"}})

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://slack.com/api/chat.postMessage",
                json={"channel": channel, "blocks": blocks, "text": "Meeting Intelligence Report"},
                headers={"Authorization": f"Bearer {token}"},
            )
        data = resp.json()
        if data.get("ok"):
            return IntegrationResult(success=True, external_id=data.get("ts"))
        return IntegrationResult(success=False, error=data.get("error"))
