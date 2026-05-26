from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ApartmentBase(BaseModel):
    lat: float = Field(..., ge=49.0, le=54.9, description="WGS-84 latitude within Poland")
    lon: float = Field(..., ge=14.1, le=24.2, description="WGS-84 longitude within Poland")
    price_per_m2: float = Field(..., gt=0, description="Price in PLN per square metre")
    area_m2: float = Field(..., gt=0, le=500)
    floor: int = Field(..., ge=0, le=50)
    build_year: int = Field(..., ge=1900, le=2030)
    centre_distance: float = Field(..., ge=0, description="Distance to city centre in km")
    city: str = Field(..., description="City slug matching cities.py")


class ApartmentCreate(ApartmentBase):
    pass


class ApartmentRead(ApartmentBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ApartmentListResponse(BaseModel):
    data: list[ApartmentRead]
    total: int
