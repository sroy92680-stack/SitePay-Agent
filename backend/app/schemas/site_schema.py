#Owner::ANIKET::ANHOTRA = MR.Panda
"""Construction site names and source-entered location descriptions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SiteCreate(BaseModel):
    """Validate human-entered physical site data without geocoding guesses."""

    name: str = Field(min_length=1, max_length=160)
    location_description: str | None = Field(default=None, max_length=1000)


class SiteResponse(BaseModel):
    """Return only the site record and its verified project association."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    location_description: str | None
