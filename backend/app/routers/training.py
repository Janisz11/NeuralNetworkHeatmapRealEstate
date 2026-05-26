import os
import pandas as pd
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.apartment import Apartment
from ..models.model_run import ModelRun
from ..schemas.model_run import TrainRequest, TrainResponse, TrainStatusResponse, ModelRunRead
from ..ml.trainer import train_model, TRAINING_STATE
from ..config import get_settings
from ..cities import CITIES

router = APIRouter(prefix="/api", tags=["training"])
settings = get_settings()


def _run_training(run_id: int, df: pd.DataFrame, req: TrainRequest, db_session):
    cities = list(CITIES.keys())
    total_epochs = req.epochs * len(cities)

    try:
        city_results = []
        for i, city in enumerate(cities):
            city_df = df[df["city"] == city].copy()
            if len(city_df) < 10:
                continue
            weights_path = os.path.join(settings.weights_dir, f"{run_id}_{city}.pt")
            result = train_model(
                run_id=run_id,
                df=city_df,
                epochs=req.epochs,
                learning_rate=req.learning_rate,
                hidden_layers=req.hidden_layers,
                weights_path=weights_path,
                epoch_offset=i * req.epochs,
                total_epochs_override=total_epochs,
            )
            city_results.append(result)

        avg_mse = sum(r["mse_loss"] for r in city_results) / len(city_results)
        avg_r2 = sum(r["r2_score"] for r in city_results) / len(city_results)

        TRAINING_STATE[run_id]["status"] = "done"
        db_session.query(ModelRun).filter(ModelRun.id == run_id).update({
            "mse_loss": round(avg_mse, 6),
            "r2_score": round(avg_r2, 4),
            "status": "done",
            "weights_path": settings.weights_dir,
        })
        db_session.commit()

    except Exception as exc:
        if run_id in TRAINING_STATE:
            TRAINING_STATE[run_id]["status"] = "error"
        db_session.query(ModelRun).filter(ModelRun.id == run_id).update({"status": "error"})
        db_session.commit()
        raise exc
    finally:
        db_session.close()


@router.post("/train", response_model=TrainResponse)
def start_training(
    req: TrainRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    apartments = db.query(Apartment).all()
    if len(apartments) < 10:
        raise HTTPException(status_code=400, detail="Need at least 10 apartments in DB to train")

    df = pd.DataFrame([{
        "lat": a.lat, "lon": a.lon,
        "price_per_m2": a.price_per_m2, "area_m2": a.area_m2,
        "floor": a.floor, "build_year": a.build_year,
        "city": a.city,
    } for a in apartments])

    run = ModelRun(
        name=req.model_name,
        epochs=req.epochs,
        learning_rate=req.learning_rate,
        status="training",
    )
    run.hidden_layers = req.hidden_layers
    db.add(run)
    db.commit()
    db.refresh(run)

    from ..database import SessionLocal
    bg_db = SessionLocal()
    background_tasks.add_task(_run_training, run.id, df, req, bg_db)

    return TrainResponse(run_id=run.id, status="training")


@router.get("/train/{run_id}/status", response_model=TrainStatusResponse)
def get_training_status(run_id: int, db: Session = Depends(get_db)):
    run = db.query(ModelRun).filter(ModelRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Model run not found")

    state = TRAINING_STATE.get(run_id, {})
    return TrainStatusResponse(
        run_id=run_id,
        status=state.get("status", run.status),
        current_epoch=state.get("current_epoch", 0),
        total_epochs=state.get("total_epochs", run.epochs),
        loss=state.get("loss", run.mse_loss),
        r2_score=state.get("r2_score", run.r2_score),
    )


@router.get("/models", response_model=list[ModelRunRead])
def list_models(db: Session = Depends(get_db)):
    runs = db.query(ModelRun).order_by(ModelRun.created_at.desc()).all()
    return [ModelRunRead(
        id=r.id, name=r.name, epochs=r.epochs, learning_rate=r.learning_rate,
        hidden_layers=r.hidden_layers, mse_loss=r.mse_loss, r2_score=r.r2_score,
        status=r.status, created_at=r.created_at,
    ) for r in runs]
