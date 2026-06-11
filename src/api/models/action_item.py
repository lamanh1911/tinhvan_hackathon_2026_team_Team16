import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.models.base import Base, now_tz, uuid_pk

if TYPE_CHECKING:
    from src.api.models.meeting_minutes import MeetingMinutes


class ActionItem(Base):
    __tablename__ = "action_items"

    id: Mapped[uuid.UUID] = uuid_pk()
    minutes_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meeting_minutes.id"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255))
    deadline: Mapped[datetime | None] = mapped_column(Date)
    created_at: Mapped[datetime] = now_tz()
    updated_at: Mapped[datetime] = now_tz()

    minutes: Mapped["MeetingMinutes"] = relationship(back_populates="action_items")
