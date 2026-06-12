"""Simplify follow-up email — preview/copy only, no direct send

Follow-up email is a saved draft the user reviews and copies manually; the system
does not send it. Drop the recipient and attachment-suggestion columns.

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("email_drafts", "attachment_suggestions")
    op.drop_column("email_drafts", "to_email")


def downgrade() -> None:
    op.add_column(
        "email_drafts",
        sa.Column("to_email", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "email_drafts",
        sa.Column("attachment_suggestions", postgresql.JSON(), nullable=True),
    )
