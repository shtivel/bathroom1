from collections.abc import Generator

from sqlmodel import Session, create_engine

from bathroom_grader.config import settings

engine = create_engine(settings.database_url, echo=False)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session, closed automatically after each request."""
    with Session(engine) as session:
        yield session
