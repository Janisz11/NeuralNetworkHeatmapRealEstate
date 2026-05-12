from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.apartment import Apartment
from ..schemas.apartment import ApartmentListResponse, ApartmentRead

router = APIRouter(prefix="/api/apartments", tags=["apartments"])


@router.get("", response_model=ApartmentListResponse)
def list_apartments(
    limit: int = Query(default=5000, le=10000),
    offset: int = Query(default=0, ge=0),
    district: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Apartment)
    if district:
        query = query.filter(Apartment.district == district)
    total = query.count()
    apartments = query.offset(offset).limit(limit).all()
    return ApartmentListResponse(
        data=[ApartmentRead.model_validate(a) for a in apartments],
        total=total,
    )
