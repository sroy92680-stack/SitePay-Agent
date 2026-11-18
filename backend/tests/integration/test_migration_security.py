#Owner::ANIKET::ANHOTRA = MR.Panda
"""Migration-level integrity and append-only enforcement regression tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError, IntegrityError

from backend.app.database import get_engine
from backend.tests.conftest import registered_account


def test_database_migrates_to_first_revision(client: TestClient) -> None:
    """A fresh migrated test database exposes the expected revision."""
    with get_engine().connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert revision == "0001"


def test_audit_update_and_delete_are_denied(client: TestClient) -> None:
    """Database triggers refuse mutation even when called outside ORM."""
    registered_account(client, "audit_owner@example.com")
    with get_engine().connect() as connection:
        event_id = connection.execute(text("SELECT id FROM audit_logs LIMIT 1")).scalar_one()
    with get_engine().begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(
                text("UPDATE audit_logs SET action='tampered' WHERE id=:id"), {"id": event_id}
            )
    with get_engine().begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(text("DELETE FROM audit_logs WHERE id=:id"), {"id": event_id})
    with get_engine().connect() as connection:
        assert connection.execute(
            text("SELECT action FROM audit_logs WHERE id=:id"), {"id": event_id}
        ).scalar_one() == "account.registered"


def test_foreign_keys_reject_invalid_tenant(client: TestClient) -> None:
    """Foreign key constraints must prevent orphan memberships."""
    with get_engine().begin() as connection:
        with pytest.raises(IntegrityError):
            connection.execute(
                text(
                    "INSERT INTO memberships (id, user_id, organization_id, role) "
                    "VALUES ('test-id', 'nonexistent', 'also-missing', 'owner')"
                )
            )
