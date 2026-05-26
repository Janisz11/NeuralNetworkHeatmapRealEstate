import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.model_run import ModelRun
from ..schemas.heatmap import HeatmapRequest, HeatmapResponse
from ..ml.inference import generate_heatmap
from ..config import get_settings

router = APIRouter(prefix="/api", tags=["inference"])
settings = get_settings()


@router.post("/heatmap", response_model=HeatmapResponse)
def get_heatmap(req: HeatmapRequest, db: Session = Depends(get_db)):
    run = db.query(ModelRun).filter(ModelRun.id == req.run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Model run not found")
    if run.status != "done":
        raise HTTPException(status_code=400, detail="Model is not ready (still training or errored)")

    weights_path = os.path.join(settings.weights_dir, f"{req.run_id}_{req.city}.pt")
    if not os.path.exists(weights_path):
        raise HTTPException(
            status_code=404,
            detail=f"Weights for city '{req.city}' not found (run_id={req.run_id})",
        )

    result = generate_heatmap(
        weights_path=weights_path,
        resolution=req.resolution,
        city=req.city,
        area_min=req.area_min,
        area_max=req.area_max,
        floor_min=req.floor_min,
        floor_max=req.floor_max,
        year_min=req.year_min,
        year_max=req.year_max,
    )
    return HeatmapResponse(**result)
