import os
import sys
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models.apartment import Apartment
from app.database import Base

Base.metadata.create_all(bind=engine)

DISTRICTS = [
    ("Stare Miasto",  51.110, 17.032, 0.010, 0.012, 14000, 16000, 160),
    ("Śródmieście",   51.105, 17.020, 0.009, 0.011, 13000, 15000, 140),
    ("Biskupin",      51.123, 17.043, 0.008, 0.010, 13000, 14500, 110),
    ("Krzyki",        51.080, 17.010, 0.015, 0.018, 12000, 14000, 150),
    ("Fabryczna",     51.100, 16.950, 0.018, 0.020, 11000, 13000, 140),
    ("Psie Pole",     51.150, 17.050, 0.018, 0.020, 10000, 12000, 130),
    ("Pawłowice",     51.065, 16.930, 0.015, 0.015,  9500, 11000,  80),
    ("Widawa",        51.165, 16.920, 0.014, 0.016, 10000, 11500,  90),
]

rng = np.random.default_rng(42)


def generate_apartments() -> list[dict]:
    rows = []
    for (district, clat, clon, lat_std, lon_std, pmin, pmax, n) in DISTRICTS:
        lats = rng.normal(clat, lat_std, n).clip(51.05, 51.18)
        lons = rng.normal(clon, lon_std, n).clip(16.87, 17.08)
        areas = rng.uniform(25, 150, n)
        floors = rng.integers(0, 12, n)
        years = rng.integers(1960, 2024, n)

        base_price = rng.uniform(pmin, pmax, n)
        year_bonus = (years - 1960) / (2024 - 1960) * (pmax - pmin) * 0.15
        floor_bonus = floors / 12 * (pmax - pmin) * 0.05
        noise = rng.normal(0, (pmax - pmin) * 0.04, n)
        prices = (base_price + year_bonus + floor_bonus + noise).clip(8000, 20000)

        for i in range(n):
            rows.append({
                "lat": round(float(lats[i]), 6),
                "lon": round(float(lons[i]), 6),
                "price_per_m2": round(float(prices[i]), 2),
                "area_m2": round(float(areas[i]), 1),
                "floor": int(floors[i]),
                "build_year": int(years[i]),
                "district": district,
            })
    return rows


def seed():
    db: Session = SessionLocal()
    try:
        existing = db.query(Apartment).count()
        if existing > 0:
            print(f"Database already has {existing} apartments — skipping seed.")
            return

        rows = generate_apartments()
        db.bulk_insert_mappings(Apartment, rows)
        db.commit()
        print(f"Seeded {len(rows)} apartments across {len(DISTRICTS)} districts.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
