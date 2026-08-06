"""Notify approvers that a meeting is ready for review (email + Slack)."""


async def notify_approver(meeting_id: str, approval_id: str, submitted_by: str, item_count: int):
    raise NotImplementedError("TODO: send email + Slack DM to the relevant approver(s)")
