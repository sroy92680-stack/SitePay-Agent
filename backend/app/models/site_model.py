#Owner::ANIKET::ANHOTRA = MR.Panda
"""Physical construction site records belonging to authenticated projects."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base_model import BaseModel, create_identifier


class Site(BaseModel):
    """Physical project site with a human-entered location description."""

    __tablename__ = "sites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_identifier)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    location_description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
