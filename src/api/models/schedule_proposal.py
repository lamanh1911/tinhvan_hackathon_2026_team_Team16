import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.api.models.base import Base, now_tz, uuid_pk


class ScheduleProposal(Base):
    __tablename__ = "schedule_proposals"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'approved')",
            name="ck_schedule_proposals_status",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    slots_json: Mapped[list | None] = mapped_column(JSON)
    approved_slot_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = now_tz()
    updated_at: Mapped[datetime] = now_tz()
