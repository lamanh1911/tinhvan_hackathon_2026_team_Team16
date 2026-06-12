import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.models.base import Base, now_tz, uuid_pk

if TYPE_CHECKING:
    from src.api.models.customer import Customer
    from src.api.models.email_draft import EmailDraft
    from src.api.models.meeting_minutes import MeetingMinutes


class Meeting(Base):
    __tablename__ = "meetings"
    __table_args__ = (
        CheckConstraint("mode IN ('online', 'offline')", name="ck_meetings_mode"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    # Nullable: a meeting may be auto-created from a transcript upload (FR-05)
    # before any customer is linked.
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True
    )
    mode: Mapped[str] = mapped_column(String(10), nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    location: Mapped[str | None] = mapped_column(Text)
    graph_event_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = now_tz()
    updated_at: Mapped[datetime] = now_tz()
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    customer: Mapped["Customer"] = relationship(back_populates="meetings")
    minutes: Mapped[list["MeetingMinutes"]] = relationship(back_populates="meeting")
    email_drafts: Mapped[list["EmailDraft"]] = relationship(back_populates="meeting")
