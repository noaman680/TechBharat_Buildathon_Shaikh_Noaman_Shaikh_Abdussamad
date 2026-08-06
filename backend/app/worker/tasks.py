"""Celery tasks that drive the LangGraph pipeline for uploaded meetings."""
from app.worker.celery import celery_app


@celery_app.task(name="app.worker.tasks.process_meeting")
def process_meeting(meeting_id: str):
    raise NotImplementedError("TODO: build initial MeetingState, invoke build_meeting_graph()")


@celery_app.task(name="app.worker.tasks.run_extraction")
def run_extraction(meeting_id: str):
    raise NotImplementedError("TODO: resume graph at the extraction node if re-triggered")
