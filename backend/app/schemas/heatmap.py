from typing import Optional
from pydantic import BaseModel, Field


class HeatmapRequest(BaseModel):
    run_id: int
    city: str = Field(default="warszawa")
    resolution: int = Field(default=100, ge=20, le=300)
    # Feature ranges — None means "use typical (p25–p75 mean from model stats)"
    area_min: Optional[float] = Field(default=None, ge=0, le=500)
    area_max: Optional[float] = Field(default=None, ge=0, le=500)
    floor_min: Optional[float] = Field(default=None, ge=0, le=50)
    floor_max: Optional[float] = Field(default=None, ge=0, le=50)
    year_min: Optional[float] = Field(default=None, ge=1900, le=2030)
    year_max: Optional[float] = Field(default=None, ge=1900, le=2030)


class HeatmapResponse(BaseModel):
    image_base64: str
    min_val: float
    max_val: float
    bounds: list[list[float]]
    # Typical market ranges from training data — used by ParameterPanel display
    area_p25: float
    area_p75: float
    floor_p25: float
    floor_p75: float
    year_p25: float
    year_p75: float
