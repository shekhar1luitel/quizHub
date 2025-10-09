"""scope categories and questions to organizations

Revision ID: 202410221010_scope_org_content
Revises: 202410220930
Create Date: 2024-10-22 10:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "202410221010_scope_org_content"
down_revision = "202410220930"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "categories",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_categories_organization_id", "categories", ["organization_id"])
    op.create_foreign_key(
        "fk_categories_organization",
        "categories",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column(
        "questions",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_questions_organization_id", "questions", ["organization_id"])
    op.create_foreign_key(
        "fk_questions_organization",
        "questions",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("categories_name_key", "categories", type_="unique")
    op.drop_constraint("categories_slug_key", "categories", type_="unique")
    op.create_unique_constraint(
        "uq_categories_org_name", "categories", ["organization_id", "name"]
    )
    op.create_unique_constraint(
        "uq_categories_org_slug", "categories", ["organization_id", "slug"]
    )
    op.create_index("ix_categories_name", "categories", ["name"])

    op.execute(
        """
        UPDATE questions
        SET organization_id = categories.organization_id
        FROM categories
        WHERE categories.id = questions.category_id
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE questions
        SET organization_id = NULL
        """
    )

    op.drop_constraint("uq_categories_org_slug", "categories", type_="unique")
    op.drop_constraint("uq_categories_org_name", "categories", type_="unique")
    op.create_unique_constraint("categories_slug_key", "categories", ["slug"])
    op.create_unique_constraint("categories_name_key", "categories", ["name"])

    op.drop_constraint("fk_questions_organization", "questions", type_="foreignkey")
    op.drop_index("ix_questions_organization_id", table_name="questions")
    op.drop_column("questions", "organization_id")

    op.drop_constraint("fk_categories_organization", "categories", type_="foreignkey")
    op.drop_index("ix_categories_organization_id", table_name="categories")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_column("categories", "organization_id")
