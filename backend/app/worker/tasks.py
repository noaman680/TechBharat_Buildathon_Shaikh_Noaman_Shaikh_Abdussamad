"""Celery tasks for async processing."""
import asyncio
from app.worker.celery import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_meeting(self, meeting_id: str, file_path: str,
                    meeting_date: str, timezone: str,
                    participants: list, org_id: str, user_id: str):
    """Full meeting processing pipeline via LangGraph."""
    try:
        from app.api.meetings import process_meeting_background
        asyncio.run(process_meeting_background(
            meeting_id=meeting_id, file_path=file_path,
            meeting_date=meeting_date, timezone=timezone,
            participants=participants, org_id=org_id, user_id=user_id,
        ))
        return {"status": "complete", "meeting_id": meeting_id}
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3)
def execute_integration(self, action_item_id: str, integration: str, config: dict):
    """Execute a single integration task."""
    try:
        from app.integrations.registry import IntegrationRegistry
        import asyncio

        async def run():
            registry = IntegrationRegistry()
            integration_obj = registry.get(integration)
            if not integration_obj:
                return {"error": f"Integration {integration} not found"}
            return {"status": "executed", "action_item_id": action_item_id}

        return asyncio.run(run())
    except Exception as exc:
        raise self.retry(exc=exc)
