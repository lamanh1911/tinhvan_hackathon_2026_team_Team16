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
    travel_buffer_minutes: int | None = None


class ScheduleOnlineRequest(BaseModel):
    customer_id: uuid.UUID | None = None
    member_ids: list[uuid.UUID] | None = None
    start_date: str | None = Field(
        default=None,
        description="ISO date string (YYYY-MM-DD). Defaults to today.",
    )


class ScheduleOfflineRequest(BaseModel):
    location: str = Field(..., min_length=1, description="Meeting location address")
    customer_id: uuid.UUID | None = None
    member_ids: list[uuid.UUID] | None = None
    start_date: str | None = Field(
        default=None,
        description="ISO date string (YYYY-MM-DD). Defaults to today.",
    )


class ScheduleProposalResponse(BaseModel):
    id: uuid.UUID
    status: str
    mode: str = "online"
    location: str | None = None
    slots: list[SlotProposal]
    approved_slot_index: int | None
    customer_id: uuid.UUID | None
    created_at: datetime


class SlotApproveRequest(BaseModel):
    slot_index: int = Field(..., ge=0)
