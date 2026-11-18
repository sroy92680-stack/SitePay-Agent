#Owner::ANIKET::ANHOTRA = MR.Panda
"""Append-only audit records with write-once ORM enforcement."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, event
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base_model import BaseModel, create_identifier, utc_timestamp


class AuditLog(BaseModel):
    """Immutable provenance for authentication and project changes."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_identifier)
    actor_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    value_before: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    value_after: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_timestamp
    )


@event.listens_for(AuditLog, "before_update")
def deny_audit_update(mapper: object, connection: object, target: AuditLog) -> None:
    """Refuse ORM updates to audit records.

    Database-level write protection is added in the PostgreSQL migration.
    """
    raise ValueError("Audit log entries cannot be updated")


@event.listens_for(AuditLog, "before_delete")
def deny_audit_delete(mapper: object, connection: object, target: AuditLog) -> None:
    """Refuse ORM deletions of audit records.

    The authoritative audit sequence is append-only.
    """
    raise ValueError("Audit log entries cannot be deleted")
