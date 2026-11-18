#Owner::ANIKET::ANHOTRA = MR.Panda
"""Create users, tenants, roles, projects, sites and protected audit records."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the initial tenant-scoped schema and deny audit modifications.

    All future schema evolution must use separately reviewed migrations.
    """
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("preferred_language", sa.String(2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("country_pack", sa.String(12), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "memberships",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"),
                  nullable=False),
        sa.Column(
            "organization_id", sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False,
        ),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.CheckConstraint(
            "status IN ('active', 'pending')",
            name="ck_memberships_status",
        ),
        sa.UniqueConstraint("user_id", "organization_id", name="uq_membership_user_org"),
        sa.CheckConstraint(
            "role IN ('owner', 'project_manager', 'site_engineer', 'accounts', 'worker')",
            name="ck_memberships_known_role",
        ),
    )
    op.create_index("ix_memberships_user_id", "memberships", ["user_id"])
    op.create_index("ix_memberships_organization_id", "memberships", ["organization_id"])
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "organization_id", sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("client_name", sa.String(160)),
        sa.Column("contract_value", sa.Numeric(18, 2)),
        sa.Column("country_pack", sa.String(12), nullable=False),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "contract_value IS NULL OR contract_value >= 0",
            name="ck_projects_contract_positive",
        ),
    )
    op.create_index("ix_projects_organization_id", "projects", ["organization_id"])
    op.create_table(
        "sites",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id", sa.String(36),
            sa.ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("location_description", sa.String(1000)),
    )
    op.create_index("ix_sites_project_id", "sites", ["project_id"])
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "actor_user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False,
        ),
        sa.Column(
            "organization_id", sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False,
        ),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(80), nullable=False),
        sa.Column("target_id", sa.String(36), nullable=False),
        sa.Column("value_before", sa.JSON()),
        sa.Column("value_after", sa.JSON()),
        sa.Column("reason", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_organization_id", "audit_logs", ["organization_id"])
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            """
            CREATE FUNCTION sitepay_reject_audit_mutation() RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION 'Audit records are immutable';
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        op.execute(
            "CREATE TRIGGER audit_immutable BEFORE UPDATE OR DELETE ON audit_logs "
            "FOR EACH ROW EXECUTE FUNCTION sitepay_reject_audit_mutation()"
        )
    elif op.get_bind().dialect.name == "sqlite":
        op.execute(
            "CREATE TRIGGER audit_immutable_update BEFORE UPDATE ON audit_logs "
            "BEGIN SELECT RAISE(ABORT, 'Audit records are immutable'); END"
        )
        op.execute(
            "CREATE TRIGGER audit_immutable_delete BEFORE DELETE ON audit_logs "
            "BEGIN SELECT RAISE(ABORT, 'Audit records are immutable'); END"
        )


def downgrade() -> None:
    """Remove the initial schema only when an operator deliberately downgrades.

    This is destructive and must never be invoked on production without backup.
    """
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TRIGGER audit_immutable ON audit_logs")
        op.execute("DROP FUNCTION sitepay_reject_audit_mutation()")
    elif op.get_bind().dialect.name == "sqlite":
        op.execute("DROP TRIGGER audit_immutable_update")
        op.execute("DROP TRIGGER audit_immutable_delete")
    op.drop_index("ix_audit_logs_organization_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_sites_project_id", table_name="sites")
    op.drop_table("sites")
    op.drop_index("ix_projects_organization_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_memberships_organization_id", table_name="memberships")
    op.drop_index("ix_memberships_user_id", table_name="memberships")
    op.drop_table("memberships")
    op.drop_table("organizations")
    op.drop_table("users")
