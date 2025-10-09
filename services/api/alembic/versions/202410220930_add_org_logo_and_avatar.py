"""add organization logo and user avatar support

Revision ID: 202410220930
Revises: 202410201630
Create Date: 2024-10-22 09:30:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = "202410220930"
down_revision = "202410201630"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "platform_users",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "organization_users",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column(
            "organization_id",
            sa.Integer(),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_organization_users_org_id", "organization_users", ["organization_id"])

    op.create_table(
        "learner_users",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column(
            "primary_org_id",
            sa.Integer(),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_learner_users_primary_org", "learner_users", ["primary_org_id"])

    op.add_column("organizations", sa.Column("logo_url", sa.String(length=512), nullable=True))
    op.add_column("user_profiles", sa.Column("avatar_url", sa.String(length=512), nullable=True))

    # backfill role tables based on current assignments
    op.execute(
        text(
            "INSERT INTO platform_users (user_id) "
            "SELECT id FROM users WHERE role IN ('admin', 'superuser')"
        )
    )
    op.execute(
        text(
            "INSERT INTO organization_users (user_id, organization_id) "
            "SELECT id, organization_id FROM users WHERE role = 'org_admin'"
        )
    )
    op.execute(
        text(
            "INSERT INTO learner_users (user_id, primary_org_id) "
            "SELECT id, organization_id FROM users WHERE role = 'user'"
        )
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "avatar_url")
    op.drop_column("organizations", "logo_url")
    op.drop_index("ix_learner_users_primary_org", table_name="learner_users")
    op.drop_table("learner_users")
    op.drop_index("ix_organization_users_org_id", table_name="organization_users")
    op.drop_table("organization_users")
    op.drop_table("platform_users")
