#Owner::ANIKET::ANHOTRA = MR.Panda
"""Authorised original ingestion with bounded content and immutable receipts."""

from __future__ import annotations

import os
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.database import get_database_session
from backend.app.dependencies import get_current_user, require_project_membership
from backend.app.models.user_model import User
from backend.app.schemas.evidence_schema import EvidenceReceipt, EvidenceResponse
from backend.app.services.evidence_service import accept_original
from backend.app.services.file_integrity_service import MAX_ORIGINAL_BYTES, validate_original
from backend.app.services.storage_service import StorageUnavailable

router = APIRouter(prefix="/projects/{project_id}/evidence", tags=["evidence"])
EVIDENCE_WRITER_ROLES = frozenset({"owner", "project_manager", "site_engineer", "worker"})


def require_evidence_preview() -> None:
    """Refuse evidence routes outside explicitly enabled development/test usage."""

    if (
        get_settings().environment not in {"development", "testing"}
        or os.getenv("SITEPAY_ENABLE_EVIDENCE_PREVIEW") != "true"
    ):
        raise HTTPException(404, "Evidence ingestion is not enabled")


@router.post("", response_model=EvidenceReceipt, status_code=201)
async def upload_original(
    project_id: str,
    response: Response,
    device_id: UUID = Form(...),
    client_record_id: UUID = Form(...),
    kind: str = Form(...),
    site_id: UUID | None = Form(None),
    captured_at: datetime | None = Form(None),
    original: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> EvidenceReceipt:
    """Accept exact bytes only after membership, signature and storage checks."""

    require_evidence_preview()
    project = require_project_membership(session, user.id, project_id, EVIDENCE_WRITER_ROLES)
    if captured_at is not None and captured_at.tzinfo is None:
        raise HTTPException(422, "Capture time must include a timezone")
    try:
        payload = await original.read(MAX_ORIGINAL_BYTES + 1)
    finally:
        await original.close()
    validated = validate_original(payload, kind)
    try:
        evidence, record, reused = accept_original(
            session,
            project=project,
            user=user,
            kind=kind,
            content=payload,
            validated=validated,
            device_id=str(device_id),
            client_record_id=str(client_record_id),
            site_id=str(site_id) if site_id else None,
            captured_at=captured_at,
        )
    except StorageUnavailable as error:
        session.rollback()
        raise HTTPException(503, str(error)) from error
    response.status_code = 200 if reused else 201
    return EvidenceReceipt(
        evidence=EvidenceResponse.model_validate(evidence),
        device_id=str(device_id),
        client_record_id=str(client_record_id),
        reused_original=reused,
        accepted_at=record.accepted_at,
    )
