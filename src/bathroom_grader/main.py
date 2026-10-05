from contextlib import asynccontextmanager

from fastapi import FastAPI

from bathroom_grader.migrations import upgrade_to_head
from bathroom_grader.routers import reviews, stations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs `alembic upgrade head` against whatever DB `config.settings.database_url`
    # points to. Fine for a single-instance local/dev setup; if this app ever runs as
    # multiple concurrent instances, move this to a separate deploy step instead, so
    # instances don't race to apply the same migration.
    upgrade_to_head()
    yield


app = FastAPI(
    title="Bathroom Grader API",
    description="Rate and discover gas station bathrooms across Israel.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(stations.router)
app.include_router(reviews.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
