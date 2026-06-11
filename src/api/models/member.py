import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from src.api.models.base import Base, now_tz, uuid_pk


class Member(Base):
    __tablename__ = "members"
    __table_args__ = (
        CheckConstraint(
            "role IN ('Sales', 'BrSE', 'Admin')",
            name="ck_members_role",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    graph_user_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = now_tz()
    updated_at: Mapped[datetime] = now_tz()
