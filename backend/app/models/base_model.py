#Owner::ANIKET::ANHOTRA = MR.Panda
"""Shared SQLAlchemy naming conventions and UUID/date constructors."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


def create_identifier() -> str:
    """Produce a non-sequential identifier for database-owned objects."""

    return str(uuid4())


def utc_timestamp() -> datetime:
    """Create an aware UTC timestamp for persisted audit metadata."""

    return datetime.now(timezone.utc)


class BaseModel(DeclarativeBase):
    """Declarative model base with stable migration-friendly names."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
