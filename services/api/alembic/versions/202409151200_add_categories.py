"""add categories and link questions"""

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
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=160), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(length=16), nullable=True),
    )

    op.add_column(
        "questions",
        sa.Column("category_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_questions_category_id",
        "questions",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    categories_table = sa.table(
        "categories",
        sa.Column("id", sa.Integer()),
        sa.Column("name", sa.String()),
        sa.Column("slug", sa.String()),
        sa.Column("description", sa.Text()),
        sa.Column("icon", sa.String()),
    )
    op.bulk_insert(
        categories_table,
        [
            {
                "id": 1,
                "name": "General",
                "slug": "general",
                "description": "Default category",
                "icon": "📝",
            }
        ],
    )

    op.execute("UPDATE questions SET category_id = 1 WHERE category_id IS NULL")
    op.alter_column("questions", "category_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.drop_constraint("fk_questions_category_id", "questions", type_="foreignkey")
    op.drop_column("questions", "category_id")
    op.drop_table("categories")
