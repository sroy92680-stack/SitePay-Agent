#Owner::ANIKET::ANHOTRA = MR.Panda
"""Source evidence and device acknowledgement API response contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class EvidenceResponse(BaseModel):
    """Return only immutable original metadata, never model-inferred progress."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    site_id: str | None
    uploaded_by: str
    kind: Literal["photo", "voice", "bill", "drawing"]
    content_type: str
    sha256: str
    size_bytes: int
    captured_at: datetime | None
    uploaded_at: datetime


class EvidenceReceipt(BaseModel):
    """An authoritative server acknowledgement for a single device operation."""

    evidence: EvidenceResponse
    device_id: str
    client_record_id: str
    reused_original: bool
    accepted_at: datetime


class EvidenceListResponse(BaseModel):
    """Return a scoped set of accepted sources, not verified measurements."""

    items: list[EvidenceResponse]
