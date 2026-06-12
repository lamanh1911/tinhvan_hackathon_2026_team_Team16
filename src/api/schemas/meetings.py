import uuid
from datetime import date, datetime

from pydantic import BaseModel

# MOM status values surfaced to the client (meeting_minutes has no 'sent' state).
MOM_STATUSES = ("draft", "in_review", "approved", "rejected")


class ActionItemSchema(BaseModel):
    id: uuid.UUID
    description: str
    owner: str | None
    deadline: date | None


class ActionItemInput(BaseModel):
    description: str
    owner: str | None = None
    deadline: date | None = None


class MOMDraftResponse(BaseModel):
    id: uuid.UUID
    meeting_id: uuid.UUID
    summary: str | None
    language: str | None
    status: str
    incomplete_warning: bool
    action_items: list[ActionItemSchema]
    created_at: datetime


class MOMUpdateRequest(BaseModel):
    summary: str | None = None
    action_items: list[ActionItemInput] | None = None


class MeetingListItem(BaseModel):
    meeting_id: uuid.UUID
    minutes_id: uuid.UUID | None
    status: str | None
    summary: str | None
    incomplete_warning: bool
    action_item_count: int
    created_at: datetime
