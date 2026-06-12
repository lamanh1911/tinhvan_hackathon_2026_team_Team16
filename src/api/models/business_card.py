import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.models.base import Base, now_tz, uuid_pk

if TYPE_CHECKING:
    from src.api.models.customer import Customer


class BusinessCard(Base):
    __tablename__ = "business_cards"

    id: Mapped[uuid.UUID] = uuid_pk()
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), index=True
    )
    image_ref: Mapped[str] = mapped_column(Text, nullable=False)
    raw_ocr_text: Mapped[str | None] = mapped_column(Text)
    fields_json: Mapped[dict | None] = mapped_column(JSON)
    confidence: Mapped[float | None] = mapped_column()
    language: Mapped[str | None] = mapped_column(String(10))
    card_type: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    created_at: Mapped[datetime] = now_tz()
    updated_at: Mapped[datetime] = now_tz()

    customer: Mapped["Customer | None"] = relationship(back_populates="business_cards")
