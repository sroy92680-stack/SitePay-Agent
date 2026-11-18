#Owner::ANIKET::ANHOTRA = MR.Panda
"""Create immutable evidence and per-device accepted operation records."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create source-of-truth metadata without altering existing projects."""

    op.create_table(
        "evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("site_id", sa.String(36), sa.ForeignKey("sites.id", ondelete="RESTRICT")),
        sa.Column(
            "uploaded_by", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("object_key", sa.String(320), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True)),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "sha256", name="uq_evidence_project_sha"),
        sa.UniqueConstraint("object_key", name="uq_evidence_object_key"),
        sa.CheckConstraint(
            "kind IN ('photo', 'voice', 'drawing', 'bill')", name="ck_evidence_kind"
        ),
        sa.CheckConstraint(
            "size_bytes > 0 AND size_bytes <= 20971520", name="ck_evidence_size"
        ),
    )
    op.create_index("ix_evidence_project_id", "evidence", ["project_id"])
    op.create_index("ix_evidence_site_id", "evidence", ["site_id"])
    op.create_table(
        "sync_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "evidence_id", sa.String(36), sa.ForeignKey("evidence.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("device_id", sa.String(36), nullable=False),
        sa.Column("client_record_id", sa.String(36), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "project_id", "device_id", "client_record_id",
            name="uq_sync_project_device_record",
        ),
    )
    op.create_index("ix_sync_records_project_id", "sync_records", ["project_id"])
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            """
            CREATE FUNCTION sitepay_deny_source_mutation() RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION 'Original evidence and acknowledgements are immutable';
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        for table_name in ("evidence", "sync_records"):
            op.execute(
                f"CREATE TRIGGER immutable_{table_name} "
                f"BEFORE UPDATE OR DELETE ON {table_name} "
                "FOR EACH ROW EXECUTE FUNCTION sitepay_deny_source_mutation()"
            )
    elif op.get_bind().dialect.name == "sqlite":
        for table_name in ("evidence", "sync_records"):
            for operation in ("UPDATE", "DELETE"):
                op.execute(
                    f"CREATE TRIGGER immutable_{table_name}_{operation.lower()} "
                    f"BEFORE {operation} ON {table_name} "
                    "BEGIN SELECT RAISE(ABORT, 'Source record is immutable'); END"
                )


def downgrade() -> None:
    """Remove tables only under a separately approved destructive rollback."""

    if op.get_bind().dialect.name == "postgresql":
        for table_name in ("evidence", "sync_records"):
            op.execute(f"DROP TRIGGER immutable_{table_name} ON {table_name}")
        op.execute("DROP FUNCTION sitepay_deny_source_mutation()")
    elif op.get_bind().dialect.name == "sqlite":
        for table_name in ("evidence", "sync_records"):
            for operation in ("update", "delete"):
                op.execute(f"DROP TRIGGER immutable_{table_name}_{operation}")
    op.drop_index("ix_sync_records_project_id", table_name="sync_records")
    op.drop_table("sync_records")
    op.drop_index("ix_evidence_site_id", table_name="evidence")
    op.drop_index("ix_evidence_project_id", table_name="evidence")
    op.drop_table("evidence")
