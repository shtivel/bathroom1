from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from bathroom_grader.database import get_session
from bathroom_grader.models import BathroomType, GasStation, Review
from bathroom_grader.schemas import ReviewCreate, ReviewRead

router = APIRouter(prefix="/stations/{station_id}/reviews", tags=["reviews"])


def _get_station_or_404(station_id: int, session: Session) -> GasStation:
    station = session.get(GasStation, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


@router.get("", response_model=list[ReviewRead])
def list_reviews(
    station_id: int,
    bathroom_type: BathroomType | None = Query(default=None),
    session: Session = Depends(get_session),
):
    _get_station_or_404(station_id, session)
    query = select(Review).where(Review.station_id == station_id)
    if bathroom_type is not None:
        query = query.where(Review.bathroom_type == bathroom_type)
    return session.exec(query).all()


@router.post("", response_model=ReviewRead, status_code=201)
def create_review(station_id: int, review: ReviewCreate, session: Session = Depends(get_session)):
    _get_station_or_404(station_id, session)
    db_review = Review.model_validate(review, update={"station_id": station_id})
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review
