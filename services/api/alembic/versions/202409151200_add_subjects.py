"""add subjects and link questions"""

from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "202409151200"
down_revision: str | None = "202409011200"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=160), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(length=16), nullable=True),
    )

    op.add_column(
        "questions",
        sa.Column("subject_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_questions_subject_id",
        "questions",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    subjects_table = sa.table(
        "subjects",
        sa.Column("id", sa.Integer()),
        sa.Column("name", sa.String()),
        sa.Column("slug", sa.String()),
        sa.Column("description", sa.Text()),
        sa.Column("icon", sa.String()),
    )
    op.bulk_insert(
        subjects_table,
        [
            {
                "id": 1,
                "name": "General",
                "slug": "general",
                "description": "Default subject",
                "icon": "📝",
            }
        ],
    )

    op.execute("UPDATE questions SET subject_id = 1 WHERE subject_id IS NULL")
    op.alter_column("questions", "subject_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.drop_constraint("fk_questions_subject_id", "questions", type_="foreignkey")
    op.drop_column("questions", "subject_id")
    op.drop_table("subjects")
