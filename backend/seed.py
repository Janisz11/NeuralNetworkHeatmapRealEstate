import os
import sys
import pandas as pd
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models.apartment import Apartment
from app.database import Base
from app.cities import CITIES

Base.metadata.create_all(bind=engine)

DATA_PATH = os.environ.get("APARTMENTS_CSV", os.path.join(os.path.dirname(__file__), "data", "apartments.csv"))


def load_apartments(path: str) -> list[dict]:
    df = pd.read_csv(path)

    df = df.dropna(subset=["buildYear", "floor", "price", "squareMeters", "centreDistance", "latitude", "longitude", "city"])
    df = df[df["squareMeters"] > 0]
    df = df[df["city"].str.strip().str.lower().isin(CITIES)]

    df["price_per_m2"] = df["price"] / df["squareMeters"]

    rows = []
    for _, r in df.iterrows():
        rows.append({
            "lat": float(r["latitude"]),
            "lon": float(r["longitude"]),
            "price_per_m2": round(float(r["price_per_m2"]), 2),
            "area_m2": round(float(r["squareMeters"]), 1),
            "floor": int(r["floor"]),
            "build_year": int(r["buildYear"]),
            "centre_distance": round(float(r["centreDistance"]), 4),
            "city": str(r["city"]).strip().lower(),
        })
    return rows


def seed():
    db: Session = SessionLocal()
    try:
        existing = db.query(Apartment).count()
        if existing > 0:
            print(f"Database already has {existing} apartments — skipping seed.")
            return

        rows = load_apartments(DATA_PATH)
        db.bulk_insert_mappings(Apartment, rows)
        db.commit()
        print(f"Seeded {len(rows)} apartments from {DATA_PATH}.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
