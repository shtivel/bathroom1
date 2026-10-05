"""Run Alembic programmatically (app startup, tests) instead of only via the `alembic` CLI."""

from pathlib import Path

from alembic import command
from alembic.config import Config

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def alembic_config() -> Config:
    config = Config(str(REPO_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "alembic"))
    return config


def upgrade_to_head() -> None:
    command.upgrade(alembic_config(), "head")
