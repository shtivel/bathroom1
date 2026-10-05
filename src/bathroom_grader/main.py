from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from bathroom_grader.database import engine
from bathroom_grader.routers import reviews, stations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev-only convenience: create tables directly from the models.
    # Once the schema stabilizes, switch to Alembic migrations instead.
    SQLModel.metadata.create_all(engine)
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
