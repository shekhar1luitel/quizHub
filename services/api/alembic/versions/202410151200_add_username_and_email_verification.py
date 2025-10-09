"""add username column and email verification tokens"""

from __future__ import annotations

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "202410151200"
down_revision: str | None = "202410010900"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _sanitize_username(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "-" for ch in value.lower())
    cleaned = cleaned.strip("-")
    return cleaned or "user"


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=150), nullable=True))

    bind = op.get_bind()
    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("email", sa.String(length=255)),
        sa.column("username", sa.String(length=150)),
    )

    existing = list(bind.execute(sa.select(users_table.c.id, users_table.c.email)))
    seen: set[str] = set()
    for row in existing:
        base = row.email.split("@", 1)[0] if row.email else f"user{row.id}"
        candidate = _sanitize_username(base)
        original = candidate
        suffix = 1
        while candidate in seen:
            suffix += 1
            candidate = f"{original}-{suffix}"
        seen.add(candidate)
        bind.execute(
            sa.update(users_table)
            .where(users_table.c.id == row.id)
            .values(username=candidate[:150])
        )

    op.alter_column("users", "username", nullable=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_email_verification_tokens_user_id",
        "email_verification_tokens",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_email_verification_tokens_user_id", table_name="email_verification_tokens"
    )
    op.drop_table("email_verification_tokens")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "username")
