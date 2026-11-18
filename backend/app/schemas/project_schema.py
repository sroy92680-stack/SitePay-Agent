#Owner::ANIKET::ANHOTRA = MR.Panda
"""Public project contracts, with explicit money validation."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProjectCreate(BaseModel):
    """Create a project with no invented contract values or dates."""

    organization_id: str
    name: str = Field(min_length=1, max_length=160)
    client_name: str | None = Field(default=None, max_length=160)
    contract_value: Decimal | None = Field(
        default=None, ge=Decimal("0"), max_digits=18, decimal_places=2
    )
    country_pack: Literal["IN"] = "IN"
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("contract_value", mode="before")
    @classmethod
    def refuse_binary_float_money(cls, value: object) -> object:
        """Require a decimal string or integer to preserve exact input value."""
        if isinstance(value, float) or isinstance(value, bool):
            raise ValueError("Contract value must be a decimal string")
        return value

    @model_validator(mode="after")
    def dates_have_valid_order(self) -> ProjectCreate:
        """Reject projects whose supplied end date precedes their start."""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("Project end date must not precede start date")
        return self


class ProjectResponse(BaseModel):
    """Expose the organisation-scoped project and optional original data."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    name: str
    client_name: str | None
    contract_value: Decimal | None
    country_pack: str
    start_date: date | None
    end_date: date | None
    created_at: datetime
