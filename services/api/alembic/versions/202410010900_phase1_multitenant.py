"""Phase 1 multi-tenant foundations"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "202410010900"
down_revision = "202409201200"
branch_labels = None
depends_on = None


organization_status_enum = sa.Enum(
    "active", "inactive", name="organization_status_enum", native_enum=False
)
user_role_enum = sa.Enum("superuser", "org_admin", "admin", "user", name="user_role", native_enum=False)
user_status_enum = sa.Enum("active", "inactive", name="user_status", native_enum=False)
org_membership_role = sa.Enum(
    "org_admin", "instructor", "member", name="org_membership_role", native_enum=False
)
org_membership_status = sa.Enum(
    "active", "invited", name="org_membership_status", native_enum=False
)
email_event_status = sa.Enum(
    "queued", "sent", "failed", name="email_event_status", native_enum=False
)
app_config_scope = sa.Enum("global", "org", name="app_config_scope", native_enum=False)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_columns = {col["name"]: col for col in inspector.get_columns("users")}

    organization_status_enum.create(bind, checkfirst=True)
    user_role_enum.create(bind, checkfirst=True)
    user_status_enum.create(bind, checkfirst=True)
    org_membership_role.create(bind, checkfirst=True)
    org_membership_status.create(bind, checkfirst=True)
    email_event_status.create(bind, checkfirst=True)
    app_config_scope.create(bind, checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False, unique=True),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("status", organization_status_enum, nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "app_configs",
        sa.Column("key", sa.String(length=255), primary_key=True),
        sa.Column("value_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("scope", app_config_scope, nullable=False, server_default="global"),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "email_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("to_email", sa.String(length=255), nullable=False),
        sa.Column("template", sa.String(length=128), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", email_event_status, nullable=False, server_default="queued"),
        sa.Column("error_msg", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_email_events_status_created", "email_events", ["status", "created_at"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.String(length=1024), nullable=False),
        sa.Column("meta_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.execute("CREATE INDEX ix_notifications_user_created ON notifications (user_id, created_at DESC)")
    op.create_index("ix_notifications_user_read", "notifications", ["user_id", "read_at"])

    op.create_table(
        "enroll_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "org_memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_role", org_membership_role, nullable=False, server_default="member"),
        sa.Column("status", org_membership_status, nullable=False, server_default="active"),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_org_membership_org_user"),
    )

    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("student_id", sa.String(length=128), nullable=True, unique=True),
        sa.Column("qr_code_uri", sa.String(length=512), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    if "role" not in user_columns:
        op.add_column("users", sa.Column("role", user_role_enum, nullable=False, server_default="user"))
    else:
        op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")
        op.alter_column(
            "users",
            "role",
            type_=user_role_enum,
            existing_type=user_columns["role"]["type"],
            existing_nullable=user_columns["role"]["nullable"],
            nullable=False,
            server_default=sa.text("'user'"),
        )
    op.add_column("users", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("status", user_status_enum, nullable=False, server_default="active"))
    op.add_column(
        "users",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_org_status", "users", ["organization_id", "status"])
    op.create_foreign_key(
        "fk_users_organization_id",
        "users",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("quizzes", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_index("ix_quizzes_org", "quizzes", ["organization_id"])
    op.create_foreign_key(
        "fk_quizzes_organization_id",
        "quizzes",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.alter_column("attempts", "submitted_at", new_column_name="finished_at")
    op.add_column("attempts", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_attempts_organization_id",
        "attempts",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        "CREATE INDEX ix_attempts_user_finished ON attempts (user_id, finished_at DESC)"
    )
    op.execute(
        "CREATE INDEX ix_attempts_org_finished ON attempts (organization_id, finished_at DESC)"
    )

    op.add_column("questions", sa.Column("topic", sa.String(length=100), nullable=True))
    op.add_column("questions", sa.Column("text_en", sa.Text(), nullable=True))
    op.add_column("questions", sa.Column("text_ne", sa.Text(), nullable=True))
    op.create_index(
        "ix_questions_subject_topic_difficulty",
        "questions",
        ["subject", "topic", "difficulty"],
    )
    op.execute(
        "CREATE INDEX ix_questions_fts ON questions USING gin (to_tsvector('simple', coalesce(text_en,'') || ' ' || coalesce(text_ne,'')))"
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_columns = {col["name"]: col for col in inspector.get_columns("users")}
    op.execute("DROP INDEX IF EXISTS ix_questions_fts")
    op.drop_index("ix_questions_subject_topic_difficulty", table_name="questions")
    op.drop_column("questions", "text_ne")
    op.drop_column("questions", "text_en")
    op.drop_column("questions", "topic")

    op.execute("DROP INDEX IF EXISTS ix_attempts_org_finished")
    op.execute("DROP INDEX IF EXISTS ix_attempts_user_finished")
    op.drop_constraint("fk_attempts_organization_id", "attempts", type_="foreignkey")
    op.drop_column("attempts", "organization_id")
    op.alter_column("attempts", "finished_at", new_column_name="submitted_at")

    op.drop_constraint("fk_quizzes_organization_id", "quizzes", type_="foreignkey")
    op.drop_index("ix_quizzes_org", table_name="quizzes")
    op.drop_column("quizzes", "organization_id")

    op.drop_constraint("fk_users_organization_id", "users", type_="foreignkey")
    op.drop_index("ix_users_org_status", table_name="users")
    op.drop_column("users", "created_at")
    op.drop_column("users", "status")
    op.drop_column("users", "organization_id")
    if "role" in user_columns:
        op.alter_column(
            "users",
            "role",
            type_=sa.String(length=50),
            existing_type=user_columns["role"]["type"],
            existing_nullable=user_columns["role"]["nullable"],
            nullable=False,
            server_default=sa.text("'user'"),
        )

    op.drop_table("user_profiles")
    op.drop_table("org_memberships")
    op.drop_table("enroll_tokens")
    op.drop_index("ix_notifications_user_read", table_name="notifications")
    op.execute("DROP INDEX IF EXISTS ix_notifications_user_created")
    op.drop_table("notifications")
    op.drop_index("ix_email_events_status_created", table_name="email_events")
    op.drop_table("email_events")
    op.drop_table("app_configs")
    op.drop_table("organizations")

    organization_status_enum.drop(op.get_bind(), checkfirst=True)
    user_role_enum.drop(op.get_bind(), checkfirst=True)
    user_status_enum.drop(op.get_bind(), checkfirst=True)
    org_membership_role.drop(op.get_bind(), checkfirst=True)
    org_membership_status.drop(op.get_bind(), checkfirst=True)
    email_event_status.drop(op.get_bind(), checkfirst=True)
    app_config_scope.drop(op.get_bind(), checkfirst=True)
