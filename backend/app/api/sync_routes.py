#Owner::ANIKET::ANHOTRA = MR.Panda
"""Check immutable server-side receipt for a device outbox operation."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.upload_routes import require_evidence_preview
from backend.app.database import get_database_session
from backend.app.dependencies import get_current_user, require_project_membership
from backend.app.models.user_model import User
from backend.app.schemas.sync_schema import SyncAcknowledgement
from backend.app.services.evidence_service import accepted_operation

router = APIRouter(prefix="/projects/{project_id}/sync", tags=["synchronisation"])


@router.get("/operations/{device_id}/{client_record_id}", response_model=SyncAcknowledgement)
def get_accepted_operation(
    project_id: str,
    device_id: UUID,
    client_record_id: UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> SyncAcknowledgement:
    """Never report a device operation as synced without a persisted receipt."""

    require_evidence_preview()
    require_project_membership(session, user.id, project_id)
    operation = accepted_operation(session, project_id, str(device_id), str(client_record_id))
    if operation is None or operation.user_id != user.id:
        raise HTTPException(404, "Device operation not acknowledged")
    return SyncAcknowledgement(
        device_id=operation.device_id,
        client_record_id=operation.client_record_id,
        evidence_id=operation.evidence_id,
        sha256=operation.sha256,
        accepted_at=operation.accepted_at,
    )
