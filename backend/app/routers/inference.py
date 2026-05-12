import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.model_run import ModelRun
from ..schemas.heatmap import HeatmapRequest, HeatmapResponse
from ..ml.inference import generate_heatmap

router = APIRouter(prefix="/api", tags=["inference"])


@router.post("/heatmap", response_model=HeatmapResponse)
def get_heatmap(req: HeatmapRequest, db: Session = Depends(get_db)):
    run = db.query(ModelRun).filter(ModelRun.id == req.run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Model run not found")
    if run.status != "done":
        raise HTTPException(status_code=400, detail="Model is not ready (still training or errored)")
    if not run.weights_path or not os.path.exists(run.weights_path):
        raise HTTPException(status_code=404, detail="Model weights file not found")

    result = generate_heatmap(
        weights_path=run.weights_path,
        resolution=req.resolution,
        area_m2=req.area_m2,
        floor=req.floor,
        build_year=req.build_year,
    )
    return HeatmapResponse(**result)
