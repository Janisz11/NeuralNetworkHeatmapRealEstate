import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

WROCLAW_LAT_MIN = 51.05
WROCLAW_LAT_MAX = 51.18
WROCLAW_LON_MIN = 16.87
WROCLAW_LON_MAX = 17.08


@dataclass
class FeatureStats:
    area_min: float = 0.0
    area_max: float = 200.0
    floor_min: float = 0.0
    floor_max: float = 20.0
    year_min: float = 1950.0
    year_max: float = 2024.0
    price_min: float = 5000.0
    price_max: float = 20000.0


def fit_stats(df: pd.DataFrame) -> FeatureStats:
    return FeatureStats(
        area_min=float(df["area_m2"].min()),
        area_max=float(df["area_m2"].max()),
        floor_min=float(df["floor"].min()),
        floor_max=float(df["floor"].max()),
        year_min=float(df["build_year"].min()),
        year_max=float(df["build_year"].max()),
        price_min=float(df["price_per_m2"].min()),
        price_max=float(df["price_per_m2"].max()),
    )


def _safe_norm(value: float, vmin: float, vmax: float) -> float:
    if vmax == vmin:
        return 0.5
    return (value - vmin) / (vmax - vmin)


def normalize_features(
    lat: float,
    lon: float,
    area_m2: float,
    floor: int,
    build_year: int,
    stats: FeatureStats,
) -> np.ndarray:
    return np.array([
        _safe_norm(lat, WROCLAW_LAT_MIN, WROCLAW_LAT_MAX),
        _safe_norm(lon, WROCLAW_LON_MIN, WROCLAW_LON_MAX),
        _safe_norm(area_m2, stats.area_min, stats.area_max),
        _safe_norm(floor, stats.floor_min, stats.floor_max),
        _safe_norm(build_year, stats.year_min, stats.year_max),
    ], dtype=np.float32)


def normalize_dataset(df: pd.DataFrame, stats: FeatureStats) -> tuple[np.ndarray, np.ndarray]:
    lat_n = (df["lat"].values - WROCLAW_LAT_MIN) / (WROCLAW_LAT_MAX - WROCLAW_LAT_MIN)
    lon_n = (df["lon"].values - WROCLAW_LON_MIN) / (WROCLAW_LON_MAX - WROCLAW_LON_MIN)
    area_n = (df["area_m2"].values - stats.area_min) / max(stats.area_max - stats.area_min, 1e-9)
    floor_n = (df["floor"].values - stats.floor_min) / max(stats.floor_max - stats.floor_min, 1e-9)
    year_n = (df["build_year"].values - stats.year_min) / max(stats.year_max - stats.year_min, 1e-9)

    X = np.column_stack([lat_n, lon_n, area_n, floor_n, year_n]).astype(np.float32)
    y = ((df["price_per_m2"].values - stats.price_min) /
         max(stats.price_max - stats.price_min, 1e-9)).astype(np.float32)

    return X, y


def denormalize_price(value: float, stats: FeatureStats) -> float:
    return value * (stats.price_max - stats.price_min) + stats.price_min
