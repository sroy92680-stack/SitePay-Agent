#Owner::ANIKET::ANHOTRA = MR.Panda
"""Immutable original site evidence with a project-scoped file fingerprint."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base_model import BaseModel, create_identifier, utc_timestamp


class Evidence(BaseModel):
    """Persist immutable source provenance, never inferred site completion."""

    __tablename__ = "evidence"
    __table_args__ = (
        UniqueConstraint("project_id", "sha256", name="uq_evidence_project_sha"),
        UniqueConstraint("object_key", name="uq_evidence_object_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_identifier)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    site_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("sites.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    uploaded_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    content_type: Mapped[str] = mapped_column(String(64), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    object_key: Mapped[str] = mapped_column(String(320), nullable=False)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_timestamp, nullable=False
    )


@event.listens_for(Evidence, "before_update")
def reject_evidence_update(mapper: object, connection: object, target: Evidence) -> None:
    """Reject ORM mutation of source evidence."""

    raise ValueError("Original evidence records are immutable")


@event.listens_for(Evidence, "before_delete")
def reject_evidence_delete(mapper: object, connection: object, target: Evidence) -> None:
    """Reject ORM deletion of source evidence."""

    raise ValueError("Original evidence records are immutable")
