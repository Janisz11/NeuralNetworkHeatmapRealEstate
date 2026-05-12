import io
import base64
import numpy as np
import torch
from PIL import Image

from .model import build_model
from .preprocessing import (
    WROCLAW_LAT_MIN, WROCLAW_LAT_MAX,
    WROCLAW_LON_MIN, WROCLAW_LON_MAX,
    normalize_features, denormalize_price, FeatureStats,
)


def _load_model(weights_path: str):
    checkpoint = torch.load(weights_path, map_location="cpu", weights_only=False)
    model = build_model(checkpoint["hidden_layers"])
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, checkpoint["stats"]


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
    area_m2: float,
    floor: int,
    build_year: int,
) -> dict:
    model, stats = _load_model(weights_path)

    lats = np.linspace(WROCLAW_LAT_MIN, WROCLAW_LAT_MAX, resolution)
    lons = np.linspace(WROCLAW_LON_MIN, WROCLAW_LON_MAX, resolution)

    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")
    lat_flat = lat_grid.flatten()
    lon_flat = lon_grid.flatten()
    n_points = len(lat_flat)

    from .preprocessing import (
        WROCLAW_LAT_MIN as LAT_MIN, WROCLAW_LAT_MAX as LAT_MAX,
        WROCLAW_LON_MIN as LON_MIN, WROCLAW_LON_MAX as LON_MAX,
    )

    lat_n = (lat_flat - LAT_MIN) / (LAT_MAX - LAT_MIN)
    lon_n = (lon_flat - LON_MIN) / (LON_MAX - LON_MIN)
    area_n = (area_m2 - stats.area_min) / max(stats.area_max - stats.area_min, 1e-9)
    floor_n = (floor - stats.floor_min) / max(stats.floor_max - stats.floor_min, 1e-9)
    year_n = (build_year - stats.year_min) / max(stats.year_max - stats.year_min, 1e-9)

    X = np.column_stack([
        lat_n, lon_n,
        np.full(n_points, area_n),
        np.full(n_points, floor_n),
        np.full(n_points, year_n),
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
        "bounds": [
            [WROCLAW_LAT_MIN, WROCLAW_LON_MIN],
            [WROCLAW_LAT_MAX, WROCLAW_LON_MAX],
        ],
    }
