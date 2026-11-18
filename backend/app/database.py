#Owner::ANIKET::ANHOTRA = MR.Panda
"""Database session lifecycle with explicit engine configuration."""

from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from backend.app.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Construct the configured SQLAlchemy engine on first use.

    No database is created or migrated during application import.
    """
    configuration = get_settings()
    connection_args = (
        {"check_same_thread": False}
        if configuration.database_url.startswith("sqlite+pysqlite:")
        else {}
    )
    engine = create_engine(
        configuration.database_url,
        pool_pre_ping=True,
        connect_args=connection_args,
    )
    if connection_args:

        @event.listens_for(engine, "connect")
        def activate_sqlite_foreign_keys(connection: object, record: object) -> None:
            """Enforce SQLite foreign key constraints per connection.

            PostgreSQL enforces foreign keys without this development-only hook.
            """
            cursor = connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()

    return engine


def get_database_session() -> Iterator[Session]:
    """Yield an isolated transaction-scoped database session.

    Roll back unfinished changes and always release the connection.
    """
    session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    with session_factory() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
