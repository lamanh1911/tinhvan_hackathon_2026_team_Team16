"""Initial schema — all 7 tables

Revision ID: 0001
Revises:
Create Date: 2026-06-11
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50)),
        sa.Column("title", sa.String(255)),
        sa.Column("address", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "members",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("graph_user_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("role IN ('Sales', 'BrSE', 'Admin')", name="ck_members_role"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "business_cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id")),
        sa.Column("image_ref", sa.Text(), nullable=False),
        sa.Column("raw_ocr_text", sa.Text()),
        sa.Column("confidence", sa.Float()),
        sa.Column("language", sa.String(10)),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_business_cards_customer_id", "business_cards", ["customer_id"])

    op.create_table(
        "meetings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("mode", sa.String(10), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True)),
        sa.Column("end_time", sa.DateTime(timezone=True)),
        sa.Column("location", sa.Text()),
        sa.Column("graph_event_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("mode IN ('online', 'offline')", name="ck_meetings_mode"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meetings_customer_id", "meetings", ["customer_id"])

    op.create_table(
        "meeting_minutes",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("meetings.id"), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("language", sa.String(10)),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("incomplete_warning", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "status IN ('draft', 'in_review', 'approved', 'rejected')",
            name="ck_meeting_minutes_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meeting_minutes_meeting_id", "meeting_minutes", ["meeting_id"])

    op.create_table(
        "action_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("minutes_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("meeting_minutes.id"), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("owner", sa.String(255)),
        sa.Column("deadline", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_action_items_minutes_id", "action_items", ["minutes_id"])

    op.create_table(
        "email_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("meetings.id"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("subject", sa.Text()),
        sa.Column("body", sa.Text()),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "status IN ('draft', 'in_review', 'approved', 'sent', 'rejected')",
            name="ck_email_drafts_status",
        ),
        sa.CheckConstraint(
            "type IN ('thank_you', 'follow_up')",
            name="ck_email_drafts_type",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_drafts_meeting_id", "email_drafts", ["meeting_id"])


def downgrade() -> None:
    op.drop_index("ix_email_drafts_meeting_id", table_name="email_drafts")
    op.drop_table("email_drafts")

    op.drop_index("ix_action_items_minutes_id", table_name="action_items")
    op.drop_table("action_items")

    op.drop_index("ix_meeting_minutes_meeting_id", table_name="meeting_minutes")
    op.drop_table("meeting_minutes")

    op.drop_index("ix_meetings_customer_id", table_name="meetings")
    op.drop_table("meetings")

    op.drop_index("ix_business_cards_customer_id", table_name="business_cards")
    op.drop_table("business_cards")

    op.drop_table("members")
    op.drop_table("customers")
