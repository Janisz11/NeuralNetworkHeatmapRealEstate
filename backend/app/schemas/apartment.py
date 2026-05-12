from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ApartmentBase(BaseModel):
    lat: float = Field(..., ge=51.0, le=51.3, description="WGS-84 latitude within Wrocław")
    lon: float = Field(..., ge=16.8, le=17.2, description="WGS-84 longitude within Wrocław")
    price_per_m2: float = Field(..., gt=0, description="Price in PLN per square metre")
    area_m2: float = Field(..., gt=0, le=500)
    floor: int = Field(..., ge=0, le=50)
    build_year: int = Field(..., ge=1900, le=2030)
    district: Optional[str] = None


class ApartmentCreate(ApartmentBase):
    pass


class ApartmentRead(ApartmentBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ApartmentListResponse(BaseModel):
    data: list[ApartmentRead]
    total: int
