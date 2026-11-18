#Owner::ANIKET::ANHOTRA = MR.Panda
"""Migrations enforce write-once provenance and device acknowledgement uniqueness."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError, IntegrityError

from backend.app.database import get_engine
from backend.tests.conftest import authentication_headers, registered_account


def test_evidence_and_sync_tables_reject_mutation(client: TestClient) -> None:
    """Database triggers reject updates/deletes independently of the API."""
    user = registered_account(client, "immutable@example.com")
    project = client.post(
        "/projects",
        json={"organization_id": user["organization_id"], "name": "Integrity project"},
        headers=authentication_headers(user),
    ).json()
    project_id = project["id"]
    now = datetime.now(UTC)
    evidence_id, record_id = str(uuid4()), str(uuid4())
    with get_engine().begin() as connection:
        connection.execute(
            text(
                "INSERT INTO evidence(id,project_id,uploaded_by,kind,content_type,"
                "sha256,size_bytes,object_key,uploaded_at) VALUES"
                "(:id,:project,:actor,'photo','image/jpeg',:sha,64,:key,:now)"
            ),
            {
                "id": evidence_id,
                "project": project_id,
                "actor": user["user"]["id"],
                "sha": "1" * 64,
                "key": "ci/synthetic/original",
                "now": now,
            },
        )
        connection.execute(
            text(
                "INSERT INTO sync_records(id,project_id,user_id,evidence_id,device_id,"
                "client_record_id,sha256,accepted_at) VALUES "
                "(:id,:project,:actor,:evidence,:device,:record,:sha,:now)"
            ),
            {
                "id": record_id,
                "project": project_id,
                "actor": user["user"]["id"],
                "evidence": evidence_id,
                "device": str(uuid4()),
                "record": str(uuid4()),
                "sha": "1" * 64,
                "now": now,
            },
        )
    for table, row_id in (("evidence", evidence_id), ("sync_records", record_id)):
        with get_engine().begin() as connection:
            with pytest.raises(DatabaseError):
                connection.execute(
                    text(f"UPDATE {table} SET sha256=:sha WHERE id=:id"),
                    {"sha": "2" * 64, "id": row_id},
                )
        with get_engine().begin() as connection:
            with pytest.raises(DatabaseError):
                connection.execute(text(f"DELETE FROM {table} WHERE id=:id"), {"id": row_id})
    with get_engine().connect() as connection:
        assert connection.scalar(
            text("SELECT sha256 FROM evidence WHERE id=:id"), {"id": evidence_id}
        ) == "1" * 64
        with pytest.raises(IntegrityError):
            connection.execute(
                text(
                    "INSERT INTO evidence(id,project_id,uploaded_by,kind,content_type,"
                    "sha256,size_bytes,object_key,uploaded_at) VALUES"
                    "(:id,:project,:actor,'photo','image/jpeg',:sha,64,:key,:now)"
                ),
                {
                    "id": str(uuid4()),
                    "project": project_id,
                    "actor": user["user"]["id"],
                    "sha": "1" * 64,
                    "key": "ci/synthetic/alternate",
                    "now": now,
                },
            )
