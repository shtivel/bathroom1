import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from bathroom_grader.logging_config import configure_logging
from bathroom_grader.migrations import upgrade_to_head
from bathroom_grader.routers import reviews, stations

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs `alembic upgrade head` against whatever DB `config.settings.database_url`
    # points to. Fine for a single-instance local/dev setup; if this app ever runs as
    # multiple concurrent instances, move this to a separate deploy step instead, so
    # instances don't race to apply the same migration.
    logger.info("Starting up: applying database migrations")
    upgrade_to_head()
    # Alembic's env.py calls fileConfig(alembic.ini), which replaces the root logger's
    # handlers with whatever alembic.ini's [logger_root] section says (just a console
    # handler) - silently dropping our file handler. Reapply our own config afterward.
    configure_logging()
    logger.info("Migrations applied, ready to serve requests")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Bathroom Grader API",
    description="Rate and discover gas station bathrooms across Israel.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(stations.router)
app.include_router(reviews.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    duration_ms = (time.monotonic() - start) * 1000
    logger.info(
        "%s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
