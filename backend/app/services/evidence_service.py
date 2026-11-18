#Owner::ANIKET::ANHOTRA = MR.Panda
"""Transaction-safe original evidence ingestion and operation idempotency."""

from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.evidence_model import Evidence
from backend.app.models.site_model import Site
from backend.app.models.sync_record_model import SyncRecord
from backend.app.models.project_model import Project
from backend.app.models.user_model import User
from backend.app.services.audit_service import record_audit
from backend.app.services.file_integrity_service import ValidatedOriginal
from backend.app.services.storage_service import read_original, store_original


def accepted_operation(
    session: Session, project_id: str, device_id: str, client_record_id: str
) -> SyncRecord | None:
    """Find the immutable acceptance of a unique client operation."""

    return session.scalar(
        select(SyncRecord).where(
            SyncRecord.project_id == project_id,
            SyncRecord.device_id == device_id,
            SyncRecord.client_record_id == client_record_id,
        )
    )


def accept_original(
    session: Session,
    *, project: Project, user: User, kind: str, content: bytes,
    validated: ValidatedOriginal, device_id: str, client_record_id: str,
    site_id: str | None, captured_at: datetime | None,
) -> tuple[Evidence, SyncRecord, bool]:
    """Persist and acknowledge an original with unique idempotency semantics.

    A DB commit is mandatory before returning success. Failed storage leaves no ack.
    """
    if site_id is not None:
        site = session.get(Site, site_id)
        if site is None or site.project_id != project.id:
            raise HTTPException(404, "Site not found in project")
    for attempt in range(2):
        previous = accepted_operation(session, project.id, device_id, client_record_id)
        if previous:
            if previous.sha256 != validated.sha256 or previous.user_id != user.id:
                raise HTTPException(409, "Device operation key was already used")
            existing = session.get(Evidence, previous.evidence_id)
            if existing is None:
                raise HTTPException(503, "Evidence acknowledgement is inconsistent")
            read_original(existing.object_key, existing.sha256, existing.size_bytes)
            return existing, previous, True
        existing = session.scalar(
            select(Evidence).where(
                Evidence.project_id == project.id, Evidence.sha256 == validated.sha256
            )
        )
        reused_original = existing is not None
        if existing:
            read_original(existing.object_key, existing.sha256, existing.size_bytes)
        else:
            key = store_original(
                content,
                organization_id=project.organization_id,
                project_id=project.id,
                checksum=validated.sha256,
                content_type=validated.content_type,
            )
            existing = Evidence(
                project_id=project.id,
                site_id=site_id,
                uploaded_by=user.id,
                kind=kind,
                content_type=validated.content_type,
                sha256=validated.sha256,
                size_bytes=validated.size_bytes,
                object_key=key,
                captured_at=captured_at,
            )
            session.add(existing)
        try:
            session.flush()
            record = SyncRecord(
                project_id=project.id,
                user_id=user.id,
                evidence_id=existing.id,
                device_id=device_id,
                client_record_id=client_record_id,
                sha256=validated.sha256,
            )
            session.add(record)
            session.flush()
            record_audit(
                session,
                actor_user_id=user.id,
                organization_id=project.organization_id,
                action="evidence.acknowledged",
                target_type="evidence",
                target_id=existing.id,
                value_after={
                    "sha256": validated.sha256, "kind": kind,
                    "device_id": device_id, "client_record_id": client_record_id,
                    "reused_original": reused_original,
                },
            )
            session.commit()
            return existing, record, reused_original
        except IntegrityError:
            session.rollback()
            if attempt == 1:
                raise HTTPException(409, "Concurrent upload conflict") from None
    raise HTTPException(409, "Evidence upload could not be acknowledged")
