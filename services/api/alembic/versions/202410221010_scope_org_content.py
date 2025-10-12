"""scope subjects and questions to organizations

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
        "subjects",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_subjects_organization_id", "subjects", ["organization_id"])
    op.create_foreign_key(
        "fk_subjects_organization",
        "subjects",
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

    op.drop_constraint("subjects_name_key", "subjects", type_="unique")
    op.drop_constraint("subjects_slug_key", "subjects", type_="unique")
    op.create_unique_constraint(
        "uq_subjects_org_name", "subjects", ["organization_id", "name"]
    )
    op.create_unique_constraint(
        "uq_subjects_org_slug", "subjects", ["organization_id", "slug"]
    )
    op.create_index("ix_subjects_name", "subjects", ["name"])

    op.execute(
        """
        UPDATE questions
        SET organization_id = subjects.organization_id
        FROM subjects
        WHERE subjects.id = questions.subject_id
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE questions
        SET organization_id = NULL
        """
    )

    op.drop_constraint("uq_subjects_org_slug", "subjects", type_="unique")
    op.drop_constraint("uq_subjects_org_name", "subjects", type_="unique")
    op.create_unique_constraint("subjects_slug_key", "subjects", ["slug"])
    op.create_unique_constraint("subjects_name_key", "subjects", ["name"])

    op.drop_constraint("fk_questions_organization", "questions", type_="foreignkey")
    op.drop_index("ix_questions_organization_id", table_name="questions")
    op.drop_column("questions", "organization_id")

    op.drop_constraint("fk_subjects_organization", "subjects", type_="foreignkey")
    op.drop_index("ix_subjects_organization_id", table_name="subjects")
    op.drop_index("ix_subjects_name", table_name="subjects")
    op.drop_column("subjects", "organization_id")
