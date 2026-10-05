import time
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from bathroom_grader.config import settings
from bathroom_grader.database import get_session

# Must happen before `bathroom_grader.main` is imported below: that import triggers
# configure_logging(), which reads settings.log_file. Redirect it to a per-run file
# (not the real dev server's logs/app.log, and not a single shared test log that
# different runs would just keep appending to and blending together).
settings.log_file = f"logs/test-{time.strftime('%Y%m%d-%H%M%S')}.log"

from bathroom_grader.main import app  # noqa: E402


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """A fresh in-memory SQLite DB per test, so tests never touch the real Postgres DB."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """A TestClient whose DB dependency is swapped for the in-memory session above.

    Deliberately NOT used as `with TestClient(app) as client`, so the app's startup
    lifespan (which creates tables on the real Postgres engine) never runs here.
    """

    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
