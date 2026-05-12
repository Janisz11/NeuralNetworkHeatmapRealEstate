import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings
from .routers import apartments, training, inference, auth

settings = get_settings()

app = FastAPI(
    title="NeuralMap Wrocław API",
    description="Neural network real estate price heatmap for Wrocław",
    version="1.0.0",
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
    return {"status": "ok", "service": "neuralmap-wroclaw"}
