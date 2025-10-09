"""add user account type column"""

from __future__ import annotations

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "202410201630"
down_revision: str | None = "202410151200"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


user_account_type_enum = sa.Enum(
    "individual",
    "organization_admin",
    "organization_member",
    "staff",
    name="user_account_type",
    native_enum=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    user_account_type_enum.create(bind, checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "account_type",
            user_account_type_enum,
            nullable=False,
            server_default="individual",
        ),
    )

    op.execute(
        "UPDATE users SET account_type = 'staff' WHERE role IN ('superuser', 'admin')"
    )
    op.execute(
        "UPDATE users SET account_type = 'organization_admin' WHERE role = 'org_admin'"
    )
    op.execute(
        "UPDATE users SET account_type = 'organization_member' "
        "WHERE role = 'user' AND organization_id IS NOT NULL"
    )

    op.create_index("ix_users_account_type", "users", ["account_type"])



def downgrade() -> None:
    op.drop_index("ix_users_account_type", table_name="users")
    op.drop_column("users", "account_type")

    bind = op.get_bind()
    user_account_type_enum.drop(bind, checkfirst=True)
