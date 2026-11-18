#Owner::ANIKET::ANHOTRA = MR.Panda
"""Construction projects anchored to a single customer organisation."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base_model import BaseModel, create_identifier, utc_timestamp


class Project(BaseModel):
    """Tenant-scoped project, with unknown contract values remaining absent."""

    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint("contract_value IS NULL OR contract_value >= 0", name="contract_positive"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_identifier)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    client_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    contract_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    country_pack: Mapped[str] = mapped_column(String(12), nullable=False, default="IN")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_timestamp
    )
