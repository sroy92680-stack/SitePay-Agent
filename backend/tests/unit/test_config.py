#Owner::ANIKET::ANHOTRA = MR.Panda
"""Security tests for environment configuration and token issuer boundaries."""

from __future__ import annotations

import pytest

from backend.app.config import get_settings


def test_missing_jwt_signing_secret_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not allow an API to start with an absent JWT signing key."""
    monkeypatch.setenv("SITEPAY_ENVIRONMENT", "testing")
    monkeypatch.setenv("SITEPAY_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.delenv("SITEPAY_JWT_SECRET", raising=False)
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="SITEPAY_JWT_SECRET"):
        get_settings()
    get_settings.cache_clear()


def test_production_rejects_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    """Require PostgreSQL for staging and production data integrity."""
    monkeypatch.setenv("SITEPAY_ENVIRONMENT", "production")
    monkeypatch.setenv("SITEPAY_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("SITEPAY_JWT_SECRET", "synthetic-test-secret-with-at-least-32-characters")
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="PostgreSQL"):
        get_settings()
    get_settings.cache_clear()


def test_wildcard_cors_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not authorise every browser origin in a tenant application."""
    monkeypatch.setenv("SITEPAY_ENVIRONMENT", "development")
    monkeypatch.setenv("SITEPAY_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("SITEPAY_JWT_SECRET", "synthetic-test-secret-with-at-least-32-characters")
    monkeypatch.setenv("SITEPAY_CORS_ORIGINS", "*")
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="Wildcard"):
        get_settings()
    get_settings.cache_clear()
