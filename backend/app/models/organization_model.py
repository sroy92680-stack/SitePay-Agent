#Owner::ANIKET::ANHOTRA = MR.Panda
"""Customer organisations are the primary tenant isolation boundary."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base_model import BaseModel, create_identifier, utc_timestamp


class Organization(BaseModel):
    """Tenant identity with country configuration independent of project data."""

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_identifier)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    country_pack: Mapped[str] = mapped_column(String(12), default="IN", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_timestamp, nullable=False
    )
