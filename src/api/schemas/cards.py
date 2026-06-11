import uuid
from datetime import datetime

from pydantic import BaseModel

CONFIDENCE_THRESHOLD = 0.7
REQUIRED_FIELDS = {"name", "company", "email"}


class FieldWithConfidence(BaseModel):
    value: str | None
    confidence: float | None
    flagged: bool


class CardFields(BaseModel):
    name: FieldWithConfidence
    company: FieldWithConfidence
    title: FieldWithConfidence
    email: FieldWithConfidence
    phone: FieldWithConfidence
    address: FieldWithConfidence


class CardScanResponse(BaseModel):
    id: uuid.UUID
    status: str
    fields: CardFields
    created_at: datetime


class CardFieldUpdateRequest(BaseModel):
    name: str | None = None
    company: str | None = None
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class CardConfirmResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    status: str
