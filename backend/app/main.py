import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings
from .routers import apartments, training, inference, auth
from .cities import CITIES

settings = get_settings()

app = FastAPI(
    title="NeuralMap Poland API",
    description="Neural network real estate price heatmap for Poland",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.include_router(apartments.router)
app.include_router(training.router)
app.include_router(inference.router)
app.include_router(auth.router)

os.makedirs(settings.weights_dir, exist_ok=True)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "neuralmap-poland"}


@app.get("/api/cities")
def list_cities():
    return [
        {
            "slug": c["slug"],
            "display_name": c["display_name"],
            "centre_lat": c["centre_lat"],
            "centre_lon": c["centre_lon"],
        }
        for c in CITIES.values()
    ]
