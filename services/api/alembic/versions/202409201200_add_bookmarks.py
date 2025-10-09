"""Add bookmarks table"""
from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202409201200"
down_revision: str | None = "202409151200"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "question_id", name="uq_bookmarks_user_question"),
    )
    op.create_index("ix_bookmarks_question_id", "bookmarks", ["question_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_bookmarks_question_id", table_name="bookmarks")
    op.drop_table("bookmarks")
