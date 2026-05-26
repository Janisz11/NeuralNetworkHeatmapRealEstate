import io
import base64
from typing import Optional
import numpy as np
import torch
from PIL import Image

from .model import build_model


def _load_model(weights_path: str):
    checkpoint = torch.load(weights_path, map_location="cpu", weights_only=False)
    model = build_model(checkpoint["hidden_layers"])
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, checkpoint["stats"]


def _resolve(lo: Optional[float], hi: Optional[float], p25: float, p75: float) -> float:
    """Return midpoint of [lo, hi], or the midpoint of [p25, p75] when either is None."""
    if lo is None or hi is None:
        return (p25 + p75) / 2.0
    return (lo + hi) / 2.0


def _price_to_rgba(normalized: float) -> tuple[int, int, int, int]:
    t = float(np.clip(normalized, 0, 1))
    if t < 0.25:
        r, g, b = 0, int(4 * t * 255), 255
    elif t < 0.5:
        r, g, b = 0, 255, int((1 - 4 * (t - 0.25)) * 255)
    elif t < 0.75:
        r, g, b = int(4 * (t - 0.5) * 255), 255, 0
    else:
        r, g, b = 255, int((1 - 4 * (t - 0.75)) * 255), 0
    return r, g, b, 180


def generate_heatmap(
    weights_path: str,
    resolution: int,
    city: str,
    area_min: Optional[float],
    area_max: Optional[float],
    floor_min: Optional[float],
    floor_max: Optional[float],
    year_min: Optional[float],
    year_max: Optional[float],
) -> dict:
    model, stats = _load_model(weights_path)

    # Resolve ranges → single representative value fed to the network
    area_m2    = _resolve(area_min, area_max, stats.area_p25, stats.area_p75)
    floor_val  = _resolve(floor_min, floor_max, stats.floor_p25, stats.floor_p75)
    year_val   = _resolve(year_min, year_max, stats.year_p25, stats.year_p75)

    lat_min, lat_max = stats.lat_min, stats.lat_max
    lon_min, lon_max = stats.lon_min, stats.lon_max

    lats = np.linspace(lat_min, lat_max, resolution)
    lons = np.linspace(lon_min, lon_max, resolution)
    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")
    lat_flat = lat_grid.flatten()
    lon_flat = lon_grid.flatten()
    n_points = len(lat_flat)

    def _vec_norm(arr: np.ndarray, vmin: float, vmax: float) -> np.ndarray:
        return np.clip((arr - vmin) / max(vmax - vmin, 1e-9), 0.0, 1.0).astype(np.float32)

    lat_n  = _vec_norm(lat_flat, lat_min, lat_max)
    lon_n  = _vec_norm(lon_flat, lon_min, lon_max)
    area_n  = float(np.clip((area_m2   - stats.area_min)  / max(stats.area_max  - stats.area_min,  1e-9), 0.0, 1.0))
    floor_n = float(np.clip((floor_val - stats.floor_min) / max(stats.floor_max - stats.floor_min, 1e-9), 0.0, 1.0))
    year_n  = float(np.clip((year_val  - stats.year_min)  / max(stats.year_max  - stats.year_min,  1e-9), 0.0, 1.0))

    # Canonical order — must match normalize_dataset: [lat_n, lon_n, area_n, floor_n, year_n]
    X = np.column_stack([
        lat_n, lon_n,
        np.full(n_points, area_n,  dtype=np.float32),
        np.full(n_points, floor_n, dtype=np.float32),
        np.full(n_points, year_n,  dtype=np.float32),
    ]).astype(np.float32)

    with torch.no_grad():
        preds_norm = model(torch.tensor(X)).squeeze().numpy()

    preds_price = preds_norm * (stats.price_max - stats.price_min) + stats.price_min
    prices_grid = preds_price.reshape(resolution, resolution)

    min_val = float(prices_grid.min())
    max_val = float(prices_grid.max())
    price_range = max_val - min_val if max_val > min_val else 1.0

    img_array = np.zeros((resolution, resolution, 4), dtype=np.uint8)
    for i in range(resolution):
        for j in range(resolution):
            norm = (prices_grid[i, j] - min_val) / price_range
            img_array[i, j] = _price_to_rgba(norm)

    img_array = np.flipud(img_array)

    img = Image.fromarray(img_array, mode="RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return {
        "image_base64": image_b64,
        "min_val": round(min_val, 2),
        "max_val": round(max_val, 2),
        "bounds": [[lat_min, lon_min], [lat_max, lon_max]],
        "area_p25": round(stats.area_p25, 1),
        "area_p75": round(stats.area_p75, 1),
        "floor_p25": round(stats.floor_p25, 0),
        "floor_p75": round(stats.floor_p75, 0),
        "year_p25": round(stats.year_p25, 0),
        "year_p75": round(stats.year_p75, 0),
    }
