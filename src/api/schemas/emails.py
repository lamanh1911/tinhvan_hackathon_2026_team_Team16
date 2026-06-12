import uuid
from datetime import datetime

from pydantic import BaseModel

EMAIL_STATUSES = ("draft", "in_review", "approved", "sent", "rejected")


class ThankYouEmailRequest(BaseModel):
    meeting_id: uuid.UUID


class FollowUpEmailRequest(BaseModel):
    meeting_id: uuid.UUID


class EmailUpdateRequest(BaseModel):
    subject: str | None = None
    body: str | None = None


class EmailDraftResponse(BaseModel):
    id: uuid.UUID
    meeting_id: uuid.UUID
    type: str
    subject: str | None
    body: str | None
    status: str
    created_at: datetime
    updated_at: datetime
