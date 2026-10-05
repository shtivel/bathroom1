from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel


class BathroomType(StrEnum):
    """Which bathroom a review is about. Inclusive on purpose: not just a men/women binary."""

    WOMEN = "women"
    MEN = "men"
    UNISEX_OR_FAMILY = "unisex_or_family"
    ACCESSIBLE = "accessible"
    OTHER = "other"


class GasStation(SQLModel, table=True):
    """A gas station that can be reviewed."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    chain: str  # e.g. Paz, Sonol, Delek, Yellow, Ten
    address: str
    city: str
    latitude: float
    longitude: float

    reviews: list["Review"] = Relationship(back_populates="station")


class Review(SQLModel, table=True):
    """A single bathroom review for a gas station."""

    id: int | None = Field(default=None, primary_key=True)
    station_id: int = Field(foreign_key="gasstation.id")

    # Store the enum's string value ("women") rather than its default member name
    # ("WOMEN"), so the DB column matches what the API actually sends/receives.
    bathroom_type: BathroomType = Field(
        sa_column=Column(
            SAEnum(BathroomType, values_callable=lambda cls: [e.value for e in cls]),
            nullable=False,
        )
    )

    cleanliness: int = Field(ge=1, le=5)
    has_soap: bool
    has_toilet_paper: bool
    is_wheelchair_accessible: bool
    has_baby_changing_table: bool
    feels_safe: bool
    comment: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    station: GasStation = Relationship(back_populates="reviews")
