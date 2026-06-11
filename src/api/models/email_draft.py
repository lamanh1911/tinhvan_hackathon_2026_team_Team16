import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.models.base import Base, now_tz, uuid_pk

if TYPE_CHECKING:
    from src.api.models.meeting import Meeting


class EmailDraft(Base):
    __tablename__ = "email_drafts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'in_review', 'approved', 'sent', 'rejected')",
            name="ck_email_drafts_status",
        ),
        CheckConstraint(
            "type IN ('thank_you', 'follow_up')",
            name="ck_email_drafts_type",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    subject: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    created_at: Mapped[datetime] = now_tz()
    updated_at: Mapped[datetime] = now_tz()

    meeting: Mapped["Meeting"] = relationship(back_populates="email_drafts")
