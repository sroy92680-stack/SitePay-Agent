#Owner::ANIKET::ANHOTRA = MR.Panda
"""Immutable server acknowledgements of individually accepted device uploads."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base_model import BaseModel, create_identifier, utc_timestamp


class SyncRecord(BaseModel):
    """Record one accepted device operation and its referenced original."""

    __tablename__ = "sync_records"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "device_id", "client_record_id",
            name="uq_sync_project_device_record",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_identifier)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    evidence_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evidence.id", ondelete="RESTRICT"), nullable=False
    )
    device_id: Mapped[str] = mapped_column(String(36), nullable=False)
    client_record_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_timestamp, nullable=False
    )


@event.listens_for(SyncRecord, "before_update")
def reject_sync_update(mapper: object, connection: object, target: SyncRecord) -> None:
    """Never alter an accepted server acknowledgement."""

    raise ValueError("Accepted device operation records are immutable")


@event.listens_for(SyncRecord, "before_delete")
def reject_sync_delete(mapper: object, connection: object, target: SyncRecord) -> None:
    """Never delete an accepted server acknowledgement."""

    raise ValueError("Accepted device operation records are immutable")
