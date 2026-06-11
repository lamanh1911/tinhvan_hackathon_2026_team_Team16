import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.models.base import Base, now_tz, uuid_pk

if TYPE_CHECKING:
    from src.api.models.action_item import ActionItem
    from src.api.models.meeting import Meeting


class MeetingMinutes(Base):
    __tablename__ = "meeting_minutes"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'in_review', 'approved', 'rejected')",
            name="ck_meeting_minutes_status",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False, index=True
    )
    summary: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    incomplete_warning: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = now_tz()
    updated_at: Mapped[datetime] = now_tz()

    meeting: Mapped["Meeting"] = relationship(back_populates="minutes")
    action_items: Mapped[list["ActionItem"]] = relationship(back_populates="minutes")
