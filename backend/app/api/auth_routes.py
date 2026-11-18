#Owner::ANIKET::ANHOTRA = MR.Panda
"""Registration, login and current-user identity endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database import get_database_session
from backend.app.dependencies import get_current_user
from backend.app.models.user_model import User
from backend.app.schemas.auth_schema import (
    LoginRequest,
    RegistrationRequest,
    RegistrationResponse,
    TokenResponse,
    UserResponse,
)
from backend.app.services.auth_service import authenticate_user, create_access_token, register_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegistrationRequest, session: Session = Depends(get_database_session)
) -> RegistrationResponse:
    """Register a tenant owner and return an expiring access token."""
    user, organization = register_user(session, request)
    return RegistrationResponse(
        access_token=create_access_token(user.id),
        user=UserResponse.model_validate(user),
        organization_id=organization.id,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest, session: Session = Depends(get_database_session)
) -> TokenResponse:
    """Authenticate an existing user without exposing stored credentials."""
    user = authenticate_user(session, str(request.email), request.password)
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> UserResponse:
    """Show only the authenticated account's public identity fields."""
    return UserResponse.model_validate(user)
