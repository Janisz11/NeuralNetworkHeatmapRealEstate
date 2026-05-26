import numpy as np
import pandas as pd
from dataclasses import dataclass


@dataclass
class FeatureStats:
    # lat/lon bounds — p0.5/p99.5 from training data
    lat_min: float = 0.0
    lat_max: float = 1.0
    lon_min: float = 0.0
    lon_max: float = 1.0
    # normalisation bounds — p1/p99 to suppress outliers
    area_min: float = 0.0
    area_max: float = 200.0
    floor_min: float = 0.0
    floor_max: float = 20.0
    year_min: float = 1950.0
    year_max: float = 2024.0
    # typical market ranges — p25/p75, exposed to frontend via HeatmapResponse
    area_p25: float = 40.0
    area_p75: float = 80.0
    floor_p25: float = 1.0
    floor_p75: float = 5.0
    year_p25: float = 1990.0
    year_p75: float = 2015.0
    # target
    price_min: float = 5000.0
    price_max: float = 30000.0


def fit_stats(df: pd.DataFrame) -> FeatureStats:
    return FeatureStats(
        lat_min=float(df["lat"].quantile(0.005)),
        lat_max=float(df["lat"].quantile(0.995)),
        lon_min=float(df["lon"].quantile(0.005)),
        lon_max=float(df["lon"].quantile(0.995)),
        area_min=float(df["area_m2"].quantile(0.01)),
        area_max=float(df["area_m2"].quantile(0.99)),
        floor_min=float(df["floor"].quantile(0.01)),
        floor_max=float(df["floor"].quantile(0.99)),
        year_min=float(df["build_year"].quantile(0.01)),
        year_max=float(df["build_year"].quantile(0.99)),
        area_p25=float(df["area_m2"].quantile(0.25)),
        area_p75=float(df["area_m2"].quantile(0.75)),
        floor_p25=float(df["floor"].quantile(0.25)),
        floor_p75=float(df["floor"].quantile(0.75)),
        year_p25=float(df["build_year"].quantile(0.25)),
        year_p75=float(df["build_year"].quantile(0.75)),
        price_min=float(df["price_per_m2"].quantile(0.01)),
        price_max=float(df["price_per_m2"].quantile(0.99)),
    )


def _clip_norm(value: float, vmin: float, vmax: float) -> float:
    if vmax == vmin:
        return 0.5
    return float(np.clip((value - vmin) / (vmax - vmin), 0.0, 1.0))


def normalize_features(
    lat: float,
    lon: float,
    area_m2: float,
    floor: int,
    build_year: int,
    stats: FeatureStats,
) -> np.ndarray:
    """Single-point feature vector. Canonical order: [lat_n, lon_n, area_n, floor_n, year_n]."""
    return np.array([
        _clip_norm(lat, stats.lat_min, stats.lat_max),
        _clip_norm(lon, stats.lon_min, stats.lon_max),
        _clip_norm(area_m2, stats.area_min, stats.area_max),
        _clip_norm(floor, stats.floor_min, stats.floor_max),
        _clip_norm(build_year, stats.year_min, stats.year_max),
    ], dtype=np.float32)


def normalize_dataset(df: pd.DataFrame, stats: FeatureStats) -> tuple[np.ndarray, np.ndarray]:
    """Vectorised normalisation. Canonical order: [lat_n, lon_n, area_n, floor_n, year_n]."""
    def _vec_norm(arr: np.ndarray, vmin: float, vmax: float) -> np.ndarray:
        return np.clip((arr - vmin) / max(vmax - vmin, 1e-9), 0.0, 1.0).astype(np.float32)

    X = np.column_stack([
        _vec_norm(df["lat"].values,        stats.lat_min,   stats.lat_max),
        _vec_norm(df["lon"].values,        stats.lon_min,   stats.lon_max),
        _vec_norm(df["area_m2"].values,    stats.area_min,  stats.area_max),
        _vec_norm(df["floor"].values,      stats.floor_min, stats.floor_max),
        _vec_norm(df["build_year"].values, stats.year_min,  stats.year_max),
    ]).astype(np.float32)

    y = np.clip(
        (df["price_per_m2"].values - stats.price_min) / max(stats.price_max - stats.price_min, 1e-9),
        0.0, 1.0,
    ).astype(np.float32)

    return X, y


def denormalize_price(value: float, stats: FeatureStats) -> float:
    return value * (stats.price_max - stats.price_min) + stats.price_min
