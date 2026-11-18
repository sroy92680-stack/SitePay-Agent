#Owner::ANIKET::ANHOTRA = MR.Panda
"""Authentication and per-tenant authorisation for every protected route."""

from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.database import get_database_session
from backend.app.models.membership_model import Membership
from backend.app.models.project_model import Project
from backend.app.models.user_model import User

BEARER_AUTHENTICATION = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(BEARER_AUTHENTICATION),
    session: Session = Depends(get_database_session),
) -> User:
    """Verify token signature, issuer, audience, expiry and active user.

    Never trust a client-supplied organisation or role claim.
    """
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    configuration = get_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            configuration.jwt_secret,
            algorithms=["HS256"],
            issuer=configuration.jwt_issuer,
            audience=configuration.jwt_audience,
            options={"require": ["sub", "iat", "exp", "iss", "aud"]},
        )
        if payload.get("type") != "access" or not isinstance(payload.get("sub"), str):
            raise jwt.InvalidTokenError("Unexpected token type")
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid or expired access token"
        ) from error
    user = session.get(User, payload["sub"])
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account not available")
    return user


def require_organization_membership(
    session: Session,
    user_id: str,
    organization_id: str,
    allowed_roles: frozenset[str] | None = None,
) -> Membership:
    """Scope user roles to the requested organisation.

    Return 404 for missing membership to avoid tenant enumeration.
    """
    membership = session.scalar(
        select(Membership).where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id,
        )
    )
    if membership is None or membership.status != "active":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")
    if allowed_roles is not None and membership.role not in allowed_roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient project permission")
    return membership


def require_project_membership(
    session: Session,
    user_id: str,
    project_id: str,
    allowed_roles: frozenset[str] | None = None,
) -> Project:
    """Resolve a project only after checking its owning tenant membership.

    The same role rules apply regardless of whether an ID was guessed.
    """
    project = session.scalar(
        select(Project)
        .join(Membership, Project.organization_id == Membership.organization_id)
        .where(
            Project.id == project_id,
            Membership.user_id == user_id,
            Membership.status == "active",
        )
    )
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    require_organization_membership(session, user_id, project.organization_id, allowed_roles)
    return project
