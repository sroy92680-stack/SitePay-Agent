#Owner::ANIKET::ANHOTRA = MR.Panda
"""Authorised organisation roles owned by a particular user and tenant."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base_model import BaseModel, create_identifier

ALLOWED_ROLES = frozenset({"owner", "project_manager", "site_engineer", "accounts", "worker"})


class Membership(BaseModel):
    """Permission binding between one user and one customer organisation."""

    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_membership_user_org"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_identifier)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
