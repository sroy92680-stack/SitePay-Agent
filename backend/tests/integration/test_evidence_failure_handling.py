#Owner::ANIKET::ANHOTRA = MR.Panda
"""Failure injection verifies failed storage never acknowledges an upload."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from backend.app.database import get_engine
from backend.app.models.evidence_model import Evidence
from backend.app.models.sync_record_model import SyncRecord
from backend.app.services.storage_service import StorageUnavailable
from backend.tests.conftest import authentication_headers, registered_account


def test_failed_storage_produces_no_ack(
    client: TestClient, monkeypatch
) -> None:
    """Database cannot claim success when S3 persistence was unavailable."""
    monkeypatch.setenv("SITEPAY_ENABLE_EVIDENCE_PREVIEW", "true")
    account = registered_account(client, "storage_failure@example.com")
    project = client.post(
        "/projects",
        headers=authentication_headers(account),
        json={"organization_id": account["organization_id"], "name": "Failure case"},
    ).json()

    def rejected_store(*args, **kwargs) -> str:
        """Inject an explicitly failed storage boundary, never fake a success."""
        raise StorageUnavailable("Could not persist original evidence")

    monkeypatch.setattr(
        "backend.app.services.evidence_service.store_original", rejected_store
    )
    response = client.post(
        f"/projects/{project['id']}/evidence",
        headers=authentication_headers(account),
        data={
            "kind": "photo",
            "device_id": str(uuid4()),
            "client_record_id": str(uuid4()),
        },
        files={
            "original": (
                "synthetic.png",
                b"\x89PNG\r\n\x1a\n" + b"\x00" * 20,
                "image/png",
            )
        },
    )
    assert response.status_code == 503
    with get_engine().connect() as connection:
        assert connection.execute(select(func.count()).select_from(Evidence)).scalar_one() == 0
        assert connection.execute(select(func.count()).select_from(SyncRecord)).scalar_one() == 0
