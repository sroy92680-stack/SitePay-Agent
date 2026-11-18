#Owner::ANIKET::ANHOTRA = MR.Panda
"""Owner-governed organisations, member roles and scoped audit history."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_database_session
from backend.app.dependencies import get_current_user, require_organization_membership
from backend.app.models.audit_log_model import AuditLog
from backend.app.models.membership_model import Membership
from backend.app.models.organization_model import Organization
from backend.app.models.user_model import User
from backend.app.schemas.organization_schema import (
    MembershipCreate,
    MembershipResponse,
    OrganizationCreate,
    OrganizationResponse,
)
from backend.app.services.audit_service import record_audit
from backend.app.services.auth_service import normalized_email

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    request: OrganizationCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> OrganizationResponse:
    """Create a new tenant and bind its creator to an owner membership."""
    organization = Organization(**request.model_dump())
    session.add(organization)
    session.flush()
    session.add(Membership(user_id=user.id, organization_id=organization.id, role="owner"))
    record_audit(
        session,
        actor_user_id=user.id,
        organization_id=organization.id,
        action="organization.created",
        target_type="organization",
        target_id=organization.id,
        value_after={"name": organization.name},
    )
    session.commit()
    return OrganizationResponse.model_validate(organization)


@router.get("", response_model=list[OrganizationResponse])
def list_organizations(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> list[OrganizationResponse]:
    """Show only organisations for which the caller has a current membership."""
    organizations = session.scalars(
        select(Organization)
        .join(Membership, Organization.id == Membership.organization_id)
        .where(Membership.user_id == user.id, Membership.status == "active")
        .order_by(Organization.name, Organization.id)
    ).all()
    return [OrganizationResponse.model_validate(organization) for organization in organizations]


@router.post(
    "/{organization_id}/members",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    organization_id: str,
    request: MembershipCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> MembershipResponse:
    """Only an organisation owner can add an existing account to a tenant."""
    require_organization_membership(session, user.id, organization_id, frozenset({"owner"}))
    invited_user = session.scalar(
        select(User).where(User.email == normalized_email(str(request.email)))
    )
    if invited_user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
    existing = session.scalar(
        select(Membership.id).where(
            Membership.user_id == invited_user.id,
            Membership.organization_id == organization_id,
        )
    )
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Membership already exists")
    membership = Membership(
        user_id=invited_user.id, organization_id=organization_id, role=request.role,
        status="pending",
    )
    session.add(membership)
    session.flush()
    record_audit(
        session,
        actor_user_id=user.id,
        organization_id=organization_id,
        action="organization.member_added",
        target_type="membership",
        target_id=membership.id,
        value_after={"user_id": invited_user.id, "role": membership.role, "status": "pending"},
    )
    session.commit()
    return MembershipResponse.model_validate(membership)


@router.get("/{organization_id}/audit", response_model=list[dict])
def list_audit_events(
    organization_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> list[dict]:
    """Allow organisation owners and managers to inspect append-only events."""
    require_organization_membership(
        session, user.id, organization_id, frozenset({"owner", "project_manager"})
    )
    events = session.scalars(
        select(AuditLog)
        .where(AuditLog.organization_id == organization_id)
        .order_by(AuditLog.created_at, AuditLog.id)
        .limit(500)
    ).all()
    return [
        {
            "id": event.id,
            "actor_user_id": event.actor_user_id,
            "action": event.action,
            "target_type": event.target_type,
            "target_id": event.target_id,
            "value_before": event.value_before,
            "value_after": event.value_after,
            "reason": event.reason,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]

@router.get("/invitations/pending", response_model=list[MembershipResponse])
def list_pending_invitations(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> list[MembershipResponse]:
    """Show pending tenant memberships to the invited account only."""
    invitations = session.scalars(
        select(Membership)
        .where(Membership.user_id == user.id, Membership.status == "pending")
        .order_by(Membership.organization_id)
    ).all()
    return [MembershipResponse.model_validate(item) for item in invitations]


@router.post("/{organization_id}/invitations/accept", response_model=MembershipResponse)
def accept_invitation(
    organization_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> MembershipResponse:
    """Activate an invited membership only after the recipient accepts it."""
    membership = session.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.organization_id == organization_id,
            Membership.status == "pending",
        )
    )
    if membership is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pending invitation not found")
    membership.status = "active"
    record_audit(
        session,
        actor_user_id=user.id,
        organization_id=organization_id,
        action="organization.invitation_accepted",
        target_type="membership",
        target_id=membership.id,
        value_before={"status": "pending"},
        value_after={"status": "active"},
    )
    session.commit()
    return MembershipResponse.model_validate(membership)
