#Owner::ANIKET::ANHOTRA = MR.Panda
"""Append-only transaction-scoped audit insertion and serialization."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.models.audit_log_model import AuditLog


def record_audit(
    session: Session,
    *,
    actor_user_id: str,
    organization_id: str,
    action: str,
    target_type: str,
    target_id: str,
    value_before: dict | None = None,
    value_after: dict | None = None,
    reason: str | None = None,
) -> AuditLog:
    """Add an audit event to the same transaction as the business action.

    The caller must commit both changes atomically, or roll them back together.
    """
    entry = AuditLog(
        actor_user_id=actor_user_id,
        organization_id=organization_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        value_before=value_before,
        value_after=value_after,
        reason=reason,
    )
    session.add(entry)
    session.flush()
    return entry
