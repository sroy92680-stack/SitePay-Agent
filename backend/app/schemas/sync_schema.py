#Owner::ANIKET::ANHOTRA = MR.Panda
"""Ack-only device operation status until the durable browser outbox exists."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SyncAcknowledgement(BaseModel):
    """Report success only for a persisted, immutable server acknowledgement."""

    status: Literal["acknowledged"] = "acknowledged"
    device_id: str
    client_record_id: str
    evidence_id: str
    sha256: str
    accepted_at: datetime
