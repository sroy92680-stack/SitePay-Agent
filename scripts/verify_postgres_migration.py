#Owner::ANIKET::ANHOTRA = MR.Panda
"""Verify the real PostgreSQL core migration and append-only protections."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import inspect, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from backend.app.database import get_engine

REQUIRED_TABLES = {
    "users", "organizations", "memberships", "projects",
    "sites", "audit_logs", "alembic_version",
}


def verify_rejection(connection: object, statement: str, parameters: dict) -> None:
    """Expect the database to reject a protected write inside a savepoint.

    A rejected write must not poison or commit the verification transaction.
    """
    savepoint = connection.begin_nested()
    try:
        connection.execute(text(statement), parameters)
    except (DBAPIError, IntegrityError):
        savepoint.rollback()
        return
    savepoint.rollback()
    raise AssertionError("Database accepted a forbidden mutation")


def verify_postgres_migration() -> None:
    """Check schema version, relational integrity and write-once audit records.

    All synthetic records are rolled back and never become customer data.
    """
    engine = get_engine()
    if engine.dialect.name != "postgresql":
        raise RuntimeError("PostgreSQL verification cannot run against SQLite")
    tables = set(inspect(engine).get_table_names())
    if not REQUIRED_TABLES.issubset(tables):
        raise AssertionError(f"Missing tables: {sorted(REQUIRED_TABLES - tables)}")
    with engine.connect() as connection:
        if connection.scalar(text("SELECT version_num FROM alembic_version")) != "0001":
            raise AssertionError("Wrong PostgreSQL migration revision")
        transaction = connection.begin()
        user_id, organization_id, audit_id = (str(uuid4()) for _ in range(3))
        try:
            connection.execute(
                text(
                    "INSERT INTO users(id,email,full_name,password_hash,preferred_language,"
                    "created_at) VALUES(:id,:email,'Test','invalid-test-only-hash','en',:now)"
                ),
                {"id": user_id, "email": f"{user_id}@example.invalid", "now": datetime.now(UTC)},
            )
            connection.execute(
                text(
                    "INSERT INTO organizations(id,name,country_pack,created_at) "
                    "VALUES(:id,'CI synthetic tenant','IN',:now)"
                ),
                {"id": organization_id, "now": datetime.now(UTC)},
            )
            connection.execute(
                text(
                    "INSERT INTO audit_logs(id,actor_user_id,organization_id,action,"
                    "target_type,target_id,created_at) "
                    "VALUES(:id,:actor,:org,'ci.checked','organization',:org,:now)"
                ),
                {
                    "id": audit_id,
                    "actor": user_id,
                    "org": organization_id,
                    "now": datetime.now(UTC),
                },
            )
            verify_rejection(
                connection,
                "UPDATE audit_logs SET action='tampered' WHERE id=:id",
                {"id": audit_id},
            )
            verify_rejection(
                connection,
                "DELETE FROM audit_logs WHERE id=:id",
                {"id": audit_id},
            )
            verify_rejection(
                connection,
                "INSERT INTO memberships(id,user_id,organization_id,role,status) "
                "VALUES(:id,'fake-user',:org,'owner','active')",
                {"id": str(uuid4()), "org": organization_id},
            )
        finally:
            transaction.rollback()
    print("PASS PostgreSQL migration, audit immutability and foreign key checks")


if __name__ == "__main__":
    verify_postgres_migration()
