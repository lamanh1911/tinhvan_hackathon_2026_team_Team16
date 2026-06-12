import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AttendeeSlotStatus(BaseModel):
    name: str
    email: str
    status: str  # "free" | "busy"


class SlotProposal(BaseModel):
    index: int
    start: datetime
    end: datetime
    attendees: list[AttendeeSlotStatus]


class ScheduleOnlineRequest(BaseModel):
    customer_id: uuid.UUID | None = None
    member_ids: list[uuid.UUID] | None = None
    start_date: str | None = Field(
        default=None,
        description="ISO date string (YYYY-MM-DD). Defaults to today.",
    )


class ScheduleProposalResponse(BaseModel):
    id: uuid.UUID
    status: str
    slots: list[SlotProposal]
    approved_slot_index: int | None
    customer_id: uuid.UUID | None
    created_at: datetime


class SlotApproveRequest(BaseModel):
    slot_index: int = Field(..., ge=0)
