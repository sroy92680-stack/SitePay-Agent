#Owner::ANIKET::ANHOTRA = MR.Panda
"""Password verification, user registration and signed access token issuance."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.models.membership_model import Membership
from backend.app.models.organization_model import Organization
from backend.app.models.user_model import User
from backend.app.schemas.auth_schema import RegistrationRequest
from backend.app.services.audit_service import record_audit

PASSWORD_HASHER = PasswordHasher()


def normalized_email(address: str) -> str:
    """Normalise the identity key before uniqueness and login checks."""

    return address.strip().casefold()


def register_user(session: Session, request: RegistrationRequest) -> tuple[User, Organization]:
    """Create user, initial organisation, owner membership and audit atomically.

    Reject duplicate emails and never expose a password or its hash.
    """
    email = normalized_email(str(request.email))
    if session.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(
        email=email,
        full_name=request.full_name,
        password_hash=PASSWORD_HASHER.hash(request.password),
        preferred_language=request.preferred_language,
    )
    organization = Organization(name=request.organization_name, country_pack="IN")
    session.add_all([user, organization])
    try:
        session.flush()
        membership = Membership(
            user_id=user.id, organization_id=organization.id, role="owner"
        )
        session.add(membership)
        record_audit(
            session,
            actor_user_id=user.id,
            organization_id=organization.id,
            action="account.registered",
            target_type="organization",
            target_id=organization.id,
            value_after={"organization_name": organization.name},
        )
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Account registration conflict") from error
    return user, organization


def authenticate_user(session: Session, email: str, password: str) -> User:
    """Validate credentials using a memory-hard Argon2 password hash.

    Respond with a generic error to avoid leaking account existence.
    """
    user = session.scalar(select(User).where(User.email == normalized_email(email)))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    try:
        verified = PASSWORD_HASHER.verify(user.password_hash, password)
    except (VerificationError, VerifyMismatchError, InvalidHashError):
        verified = False
    if not verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return user


def create_access_token(user_id: str) -> str:
    """Create an expiring, audience-bound JWT for the validated account.

    Only the server may issue tokens; membership roles are rechecked in the DB.
    """
    configuration = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iss": configuration.jwt_issuer,
        "aud": configuration.jwt_audience,
        "iat": now,
        "exp": now + timedelta(minutes=configuration.jwt_minutes),
        "type": "access",
    }
    return jwt.encode(payload, configuration.jwt_secret, algorithm="HS256")
