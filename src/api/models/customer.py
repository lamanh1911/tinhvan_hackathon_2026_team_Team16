import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.models.base import Base, now_tz, uuid_pk

if TYPE_CHECKING:
    from src.api.models.business_card import BusinessCard
    from src.api.models.meeting import Meeting


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    title: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = now_tz()
    updated_at: Mapped[datetime] = now_tz()
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    business_cards: Mapped[list["BusinessCard"]] = relationship(back_populates="customer")
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="customer")
