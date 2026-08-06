"""SQLAlchemy models for MeetMind."""
from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import (
    String, Text, Float, Integer, Boolean, DateTime,
    ForeignKey, JSON, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255))
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    integrations: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Meeting(Base):
    __tablename__ = "meetings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    title: Mapped[Optional[str]] = mapped_column(String(500))
    meeting_date: Mapped[str] = mapped_column(String(20), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    input_type: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_file_url: Mapped[Optional[str]] = mapped_column(Text)
    transcript_raw: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10), default="en")
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), unique=True)
    processing_status: Mapped[str] = mapped_column(String(20), default="pending")
    langgraph_thread_id: Mapped[Optional[str]] = mapped_column(String(100))
    participants: Mapped[list] = mapped_column(JSON, default=list)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    organization: Mapped["Organization"] = relationship(back_populates="meetings")
    action_items: Mapped[list["ActionItemModel"]] = relationship(back_populates="meeting")
    report: Mapped[Optional["MeetingReport"]] = relationship(back_populates="meeting", uselist=False)


class MeetingReport(Base):
    __tablename__ = "meeting_reports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id"), unique=True)
    executive_summary: Mapped[Optional[str]] = mapped_column(Text)
    decisions: Mapped[list] = mapped_column(JSON, default=list)
    open_questions: Mapped[list] = mapped_column(JSON, default=list)
    risks: Mapped[list] = mapped_column(JSON, default=list)
    key_insights: Mapped[list] = mapped_column(JSON, default=list)
    follow_ups: Mapped[list] = mapped_column(JSON, default=list)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    meeting: Mapped["Meeting"] = relationship(back_populates="report")


class ActionItemModel(Base):
    __tablename__ = "action_items"
    __table_args__ = (UniqueConstraint("fingerprint", "org_id", name="uq_fingerprint_org"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id"), nullable=False)
    org_id: Mapped[str] = mapped_column(String(36), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_raw: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    owner_name: Mapped[Optional[str]] = mapped_column(String(255))
    owner_email: Mapped[Optional[str]] = mapped_column(String(255))
    owner_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    due_date_raw: Mapped[Optional[str]] = mapped_column(String(255))
    due_date_resolved: Mapped[Optional[str]] = mapped_column(String(20))
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_timestamp: Mapped[Optional[str]] = mapped_column(String(20))
    evidence_quote: Mapped[Optional[str]] = mapped_column(Text)
    meeting_section: Mapped[Optional[str]] = mapped_column(String(255))
    dependencies: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    external_refs: Mapped[dict] = mapped_column(JSON, default=dict)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    meeting: Mapped["Meeting"] = relationship(back_populates="action_items")


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id: Mapped[Optional[str]] = mapped_column(ForeignKey("meetings.id"))
    org_id: Mapped[Optional[str]] = mapped_column(String(36))
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    output_summary: Mapped[Optional[str]] = mapped_column(Text)
    reasoning: Mapped[Optional[str]] = mapped_column(Text)
    tool_calls: Mapped[list] = mapped_column(JSON, default=list)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExecutionResultModel(Base):
    __tablename__ = "execution_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_item_id: Mapped[str] = mapped_column(ForeignKey("action_items.id"))
    integration: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255))
    external_url: Mapped[Optional[str]] = mapped_column(Text)
    request_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    response_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def create_tables():
    from sqlalchemy.ext.asyncio import create_async_engine
    from app.config import settings
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
