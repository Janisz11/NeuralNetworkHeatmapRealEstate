from pydantic import BaseModel, Field


class HeatmapRequest(BaseModel):
    run_id: int
    resolution: int = Field(default=100, ge=20, le=300, description="Grid points per axis (NxN)")
    area_m2: float = Field(default=55.0, gt=0, le=500)
    floor: int = Field(default=3, ge=0, le=50)
    build_year: int = Field(default=2010, ge=1900, le=2030)


class HeatmapResponse(BaseModel):
    image_base64: str
    min_val: float
    max_val: float
    bounds: list[list[float]]
