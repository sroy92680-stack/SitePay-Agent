#Owner::ANIKET::ANHOTRA = MR.Panda
"""Authorised original ingestion with bounded content and immutable receipts."""

from __future__ import annotations

import os
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.database import get_database_session
from backend.app.dependencies import get_current_user, require_project_membership
from backend.app.models.evidence_model import Evidence
from backend.app.models.user_model import User
from backend.app.schemas.evidence_schema import EvidenceListResponse, EvidenceReceipt, EvidenceResponse
from backend.app.services.evidence_service import accept_original
from backend.app.services.file_integrity_service import MAX_ORIGINAL_BYTES, validate_original
from backend.app.services.storage_service import StorageUnavailable, read_original

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


@router.get("", response_model=EvidenceListResponse)
def list_project_evidence(
    project_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> EvidenceListResponse:
    """Read only accepted immutable evidence for one authorised project."""

    require_evidence_preview()
    require_project_membership(session, user.id, project_id)
    evidence = session.scalars(
        select(Evidence)
        .where(Evidence.project_id == project_id)
        .order_by(Evidence.uploaded_at.desc(), Evidence.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return EvidenceListResponse(
        items=[EvidenceResponse.model_validate(item) for item in evidence]
    )


@router.get("/{evidence_id}", response_model=EvidenceResponse)
def get_evidence_metadata(
    project_id: str,
    evidence_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> EvidenceResponse:
    """Reject guessed cross-project IDs even for valid signed users."""

    require_evidence_preview()
    require_project_membership(session, user.id, project_id)
    evidence = session.scalar(
        select(Evidence).where(Evidence.id == evidence_id, Evidence.project_id == project_id)
    )
    if evidence is None:
        raise HTTPException(404, "Evidence not found")
    return EvidenceResponse.model_validate(evidence)


@router.get("/{evidence_id}/content")
def download_original(
    project_id: str,
    evidence_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> Response:
    """Return verified original bytes as an attachment, never inline active content."""

    require_evidence_preview()
    require_project_membership(session, user.id, project_id)
    evidence = session.scalar(
        select(Evidence).where(Evidence.id == evidence_id, Evidence.project_id == project_id)
    )
    if evidence is None:
        raise HTTPException(404, "Evidence not found")
    try:
        content = read_original(evidence.object_key, evidence.sha256, evidence.size_bytes)
    except StorageUnavailable as error:
        raise HTTPException(503, str(error)) from error
    return Response(
        content=content,
        media_type=evidence.content_type,
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Disposition": f'attachment; filename="evidence-{evidence.id}"',
        },
    )
