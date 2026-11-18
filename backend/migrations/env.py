#Owner::ANIKET::ANHOTRA = MR.Panda
"""Alembic environment sharing the application's validated database URL."""

from __future__ import annotations

from alembic import context
from sqlalchemy import engine_from_config, pool

from backend.app.config import get_settings
from backend.app.models import BaseModel

configuration = context.config
target_metadata = BaseModel.metadata


def run_migrations_offline() -> None:
    """Render migrations using configured connection and metadata.

    Offline runs do not open a connection to the database.
    """
    url = get_settings().database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply versioned migrations in a transaction with explicit URL.

    Do not create, drop or modify tables automatically on API startup.
    """
    connectable = engine_from_config(
        {"sqlalchemy.url": get_settings().database_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
