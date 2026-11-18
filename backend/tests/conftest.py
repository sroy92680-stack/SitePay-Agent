#Owner::ANIKET::ANHOTRA = MR.Panda
"""Integration fixtures using real Alembic migrations and an isolated database."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from backend.app.config import get_settings
from backend.app.database import get_engine
from backend.app.main import create_application


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Start the full API on a migrated fresh SQLite database for each test.

    No test data or credentials are sent outside the test process.
    """
    database_path = tmp_path / "test_sitepay.sqlite3"
    monkeypatch.setenv(
        "SITEPAY_DATABASE_URL", f"sqlite+pysqlite:///{database_path.as_posix()}"
    )
    monkeypatch.setenv("SITEPAY_JWT_SECRET", "test-only-never-use-in-production-2026-key")
    monkeypatch.setenv("SITEPAY_ENVIRONMENT", "testing")
    monkeypatch.delenv("SITEPAY_CORS_ORIGINS", raising=False)
    get_settings.cache_clear()
    get_engine.cache_clear()
    migration_config = Config("backend/alembic.ini")
    command.upgrade(migration_config, "head")
    with TestClient(create_application()) as test_client:
        yield test_client
    get_engine().dispose()
    get_engine.cache_clear()
    get_settings.cache_clear()


def registered_account(
    client: TestClient, email: str, organization_name: str = "Test Contractor"
) -> dict:
    """Register a permissioned synthetic account and return API payload.

    This record is test data, never a real customer identity.
    """
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery-staple",
            "full_name": "Test Engineer",
            "organization_name": organization_name,
            "preferred_language": "en",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def authentication_headers(account: dict) -> dict[str, str]:
    """Return the bearer header for a response from registration."""
    return {"Authorization": f"Bearer {account['access_token']}"}
