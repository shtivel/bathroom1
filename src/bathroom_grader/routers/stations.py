from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from bathroom_grader.database import get_session
from bathroom_grader.models import BathroomType, GasStation
from bathroom_grader.schemas import GasStationCreate, GasStationRead, GasStationWithStats

router = APIRouter(prefix="/stations", tags=["stations"])


def _with_stats(
    station: GasStation, bathroom_type: BathroomType | None = None
) -> GasStationWithStats:
    reviews = station.reviews
    if bathroom_type is not None:
        reviews = [r for r in reviews if r.bathroom_type == bathroom_type]

    review_count = len(reviews)
    average_cleanliness = (
        sum(r.cleanliness for r in reviews) / review_count if review_count else None
    )
    return GasStationWithStats(
        **station.model_dump(),
        review_count=review_count,
        average_cleanliness=average_cleanliness,
    )


@router.get("", response_model=list[GasStationWithStats])
def list_stations(
    city: str | None = Query(default=None),
    bathroom_type: BathroomType | None = Query(
        default=None, description="Only factor in reviews of this bathroom type into the stats."
    ),
    session: Session = Depends(get_session),
):
    query = select(GasStation)
    if city:
        query = query.where(GasStation.city == city)
    stations = session.exec(query).all()
    return [_with_stats(station, bathroom_type) for station in stations]


@router.post("", response_model=GasStationRead, status_code=201)
def create_station(station: GasStationCreate, session: Session = Depends(get_session)):
    db_station = GasStation.model_validate(station)
    session.add(db_station)
    session.commit()
    session.refresh(db_station)
    return db_station


@router.get("/{station_id}", response_model=GasStationWithStats)
def get_station(
    station_id: int,
    bathroom_type: BathroomType | None = Query(default=None),
    session: Session = Depends(get_session),
):
    station = session.get(GasStation, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return _with_stats(station, bathroom_type)
