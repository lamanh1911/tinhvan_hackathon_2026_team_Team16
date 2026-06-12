"""MOM + follow-up email support

- Allow meetings.customer_id to be NULL (meeting auto-created from a transcript
  upload before a customer is linked).
- Add email_drafts.to_email (recipient for real send).
- Add email_drafts.attachment_suggestions (JSON list of suggested attachments).

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "meetings",
        "customer_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.add_column(
        "email_drafts",
        sa.Column("to_email", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "email_drafts",
        sa.Column("attachment_suggestions", postgresql.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("email_drafts", "attachment_suggestions")
    op.drop_column("email_drafts", "to_email")
    op.alter_column(
        "meetings",
        "customer_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
