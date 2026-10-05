from datetime import datetime

from pydantic import BaseModel, Field

from bathroom_grader.models import BathroomType


class ReviewCreate(BaseModel):
    bathroom_type: BathroomType
    cleanliness: int = Field(ge=1, le=5)
    has_soap: bool
    has_toilet_paper: bool
    is_wheelchair_accessible: bool
    has_baby_changing_table: bool
    feels_safe: bool
    comment: str | None = None


class ReviewRead(ReviewCreate):
    id: int
    station_id: int
    created_at: datetime


class GasStationCreate(BaseModel):
    name: str
    chain: str
    address: str
    city: str
    latitude: float
    longitude: float


class GasStationRead(GasStationCreate):
    id: int


class GasStationWithStats(GasStationRead):
    review_count: int
    average_cleanliness: float | None = None
