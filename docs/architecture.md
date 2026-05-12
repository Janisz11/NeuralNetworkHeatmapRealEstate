# NeuralMap Wrocław — Architecture

## Overview

Full-stack web application that trains a neural network on real estate price data
for Wrocław, Poland, and visualizes the learned spatial price distribution as an
interactive heatmap overlaid on a Leaflet.js map.

---

## Backend (FastAPI + PyTorch)

**Pattern: MVC**

| Layer | Technology | Responsibility |
|-------|-----------|----------------|
| Controller | FastAPI Routers | HTTP routing, request validation, auth checks |
| Model | SQLAlchemy ORM | Database entities (Apartment, ModelRun, User) |
| View | Pydantic schemas | Serialization / deserialization of API payloads |

**ML Pipeline:**
1. Raw data fetched from PostgreSQL as pandas DataFrame
2. `preprocessing.py` normalizes all features to [0, 1]
3. `model.py` defines a configurable MLP (default: 5 → 64 → 32 → 1)
4. `trainer.py` runs Adam optimizer with ReduceLROnPlateau scheduler
5. `inference.py` scans a 100×100 grid over the Wrocław bbox, renders PNG via Pillow

**Async training:** FastAPI BackgroundTasks + in-memory TRAINING_STATE dict.
The frontend polls `/api/train/{id}/status` every 2s.

---

## Frontend (React 18 + TypeScript)

**Pattern: component-based with custom hooks**

| Component | Role |
|-----------|------|
| `MapView` | Leaflet map container, Wrocław bbox |
| `HeatmapOverlay` | `L.imageOverlay` for base64 PNG |
| `DataPoints` | Training data circles with price colour-coding |
| `ParameterPanel` | Sliders (m², floor, year) → debounced heatmap fetch |
| `TrainingPanel` | Training form + live progress bar |
| `ModelSelector` | Dropdown of completed model runs |
| `LossChart` | Recharts line chart of epoch MSE |
| `AdminPanel` | SSO-protected model run history |

**Key hooks:**
- `useHeatmap` — 300ms debounce, fetches new PNG when slider changes
- `useTraining` — manages training lifecycle + polls status

---

## Database (PostgreSQL 15)

Three tables; migrations managed by Alembic:
- `0001_initial_schema` — creates all three tables
- `0002_add_spatial_index` — composite index on (lat, lon)

---

## Auth (Google OAuth 2.0)

Authlib + Starlette sessions for OAuth state.
On callback: upsert User row, issue HS256 JWT (1h TTL).
Protected routes use `HTTPBearer` + `jose` JWT decoding.

---

## DevOps

```
docker-compose.yml
├── postgres:15-alpine       (port 5432)
├── backend:python3.11-slim  (port 8000) — runs alembic + seed + uvicorn
└── frontend:nginx-alpine    (port 80)   — proxies /api/ and /auth/ to backend
```

GitHub Actions CI (`.github/workflows/ci.yml`):
1. `backend-lint-test` — runs migrations + seed against real Postgres service
2. `frontend-lint-build` — TypeScript check + Vite production build
3. `docker-build` — verifies both Dockerfiles compile

---

## Neural Network Details

```
Input:   [lat_norm, lon_norm, area_m2_norm, floor_norm, year_norm]  (5 features)
Hidden:  Linear(5→64) → ReLU → Dropout(0.2) → Linear(64→32) → ReLU → Dropout(0.2)
Output:  Linear(32→1)  →  predicted price/m² (denormalized)

Loss:    MSE
Optimizer: Adam (default lr=0.001)
Scheduler: ReduceLROnPlateau (patience=20, factor=0.5)
Batch:   32 samples
Split:   80% train / 20% validation
```

The network learns spatial correlations between geographic position and price —
exactly what the heatmap visualizes.
