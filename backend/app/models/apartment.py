from sqlalchemy import Column, Integer, Float, String, DateTime, func
from ..database import Base


class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    price_per_m2 = Column(Float, nullable=False)
    area_m2 = Column(Float, nullable=False)
    floor = Column(Integer, nullable=False)
    build_year = Column(Integer, nullable=False)
    district = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
