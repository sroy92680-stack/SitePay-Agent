#Owner::ANIKET::ANHOTRA = MR.Panda
"""Organisation ownership and membership request/response contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationCreate(BaseModel):
    """Create a tenant under the current authenticated account."""

    name: str = Field(min_length=1, max_length=160)
    country_pack: Literal["IN"] = "IN"


class OrganizationResponse(BaseModel):
    """Expose tenant metadata without unrelated customer records."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    country_pack: str


class MembershipCreate(BaseModel):
    """Allow owner assignment only of supported, explicit roles."""

    email: EmailStr
    role: Literal["owner", "project_manager", "site_engineer", "accounts", "worker"]


class MembershipResponse(BaseModel):
    """Expose a role assignment without secret account details."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    organization_id: str
    role: str
