"""add schedule_proposals table

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "schedule_proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("slots_json", postgresql.JSON(), nullable=True),
        sa.Column("approved_slot_index", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('draft', 'approved')", name="ck_schedule_proposals_status"),
    )
    op.create_index("ix_schedule_proposals_customer_id", "schedule_proposals", ["customer_id"])


def downgrade() -> None:
    op.drop_index("ix_schedule_proposals_customer_id", table_name="schedule_proposals")
    op.drop_table("schedule_proposals")
