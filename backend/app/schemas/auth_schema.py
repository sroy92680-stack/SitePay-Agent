#Owner::ANIKET::ANHOTRA = MR.Panda
"""Constrained authentication request and public response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegistrationRequest(BaseModel):
    """Validate one initial account and tenant registration."""

    email: EmailStr
    password: str = Field(min_length=12, max_length=256)
    full_name: str = Field(min_length=1, max_length=160)
    organization_name: str = Field(min_length=1, max_length=160)
    preferred_language: Literal["en", "hi"] = "en"


class LoginRequest(BaseModel):
    """Accept only email and password credentials for login."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class UserResponse(BaseModel):
    """Serialize public user fields only, excluding password hashes."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str
    preferred_language: str


class TokenResponse(BaseModel):
    """Return a short-lived access token and its intended type."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class RegistrationResponse(TokenResponse):
    """Return an initial owner account and its new organisation."""

    user: UserResponse
    organization_id: str
