"""Tests for the Alembic migration history itself (not the API).

These exercise real `alembic upgrade`/`downgrade` against a throwaway Postgres
database (`bathroom_grader_test`) - never the real dev DB - since they're
checking actual DDL, not just application logic. Requires a local Postgres
server, same as the rest of local dev (see CLAUDE.md).
"""

import psycopg
import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect
from sqlmodel import SQLModel

from bathroom_grader.config import settings
from bathroom_grader.migrations import alembic_config

TEST_DB_NAME = "bathroom_grader_test"
TEST_DB_URL = f"postgresql+psycopg://localhost/{TEST_DB_NAME}"


def _run_admin_sql(sql: str) -> None:
    with psycopg.connect("dbname=postgres", autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(sql)


@pytest.fixture
def migrated_db(monkeypatch):
    """Fresh throwaway Postgres DB, migrated to head exactly like env.py would for real."""
    # env.py reads the DB URL from this same settings object, so patching it here
    # is what redirects `alembic upgrade`/`downgrade` at our throwaway DB instead
    # of the real dev DB.
    monkeypatch.setattr(settings, "database_url", TEST_DB_URL)

    _run_admin_sql(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
    _run_admin_sql(f'CREATE DATABASE "{TEST_DB_NAME}"')

    config = alembic_config()
    command.upgrade(config, "head")
    engine = create_engine(TEST_DB_URL)
    try:
        yield engine, config
    finally:
        engine.dispose()
        _run_admin_sql(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')


def test_upgrade_head_creates_expected_tables(migrated_db):
    engine, _config = migrated_db
    table_names = set(inspect(engine).get_table_names())
    assert {"gasstation", "review"}.issubset(table_names)


def test_downgrade_base_removes_tables(migrated_db):
    engine, config = migrated_db
    command.downgrade(config, "base")
    table_names = set(inspect(engine).get_table_names())
    assert "gasstation" not in table_names
    assert "review" not in table_names


def test_models_have_no_pending_migration(migrated_db):
    """Drift check: fails if models.py was changed without regenerating a migration.

    If this fails, run `alembic revision --autogenerate -m "..."` and commit the result.
    """
    engine, _config = migrated_db
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        diff = compare_metadata(context, SQLModel.metadata)
    assert diff == []
