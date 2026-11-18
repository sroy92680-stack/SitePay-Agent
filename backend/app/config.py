#Owner::ANIKET::ANHOTRA = MR.Panda
"""Validated settings for API, database and token security."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Validated runtime configuration loaded from process environment."""

    environment: str
    database_url: str
    jwt_secret: str
    jwt_issuer: str
    jwt_audience: str
    jwt_minutes: int
    cors_origins: tuple[str, ...]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Read and validate runtime settings without unsafe credential defaults.

    Production and development alike require an explicit secret and database.
    """
    environment = os.getenv("SITEPAY_ENVIRONMENT", "development")
    if environment not in {"development", "testing", "staging", "production"}:
        raise ValueError("Invalid SITEPAY_ENVIRONMENT")
    database_url = os.getenv("SITEPAY_DATABASE_URL", "")
    if not database_url.startswith(("postgresql+", "sqlite+pysqlite:")):
        raise ValueError("SITEPAY_DATABASE_URL must use PostgreSQL or local SQLite")
    if environment in {"staging", "production"} and not database_url.startswith("postgresql+"):
        raise ValueError("Staging and production require PostgreSQL")
    secret = os.getenv("SITEPAY_JWT_SECRET", "")
    if len(secret) < 32:
        raise ValueError("SITEPAY_JWT_SECRET must contain at least 32 characters")
    minutes_text = os.getenv("SITEPAY_JWT_MINUTES", "30")
    minutes = int(minutes_text)
    if not 1 <= minutes <= 120:
        raise ValueError("SITEPAY_JWT_MINUTES must be 1 to 120")
    origins = tuple(
        item.strip()
        for item in os.getenv("SITEPAY_CORS_ORIGINS", "").split(",")
        if item.strip()
    )
    if "*" in origins:
        raise ValueError("Wildcard CORS origins are not allowed")
    return Settings(
        environment=environment,
        database_url=database_url,
        jwt_secret=secret,
        jwt_issuer="sitepay-agent",
        jwt_audience="sitepay-api",
        jwt_minutes=minutes,
        cors_origins=origins,
    )
