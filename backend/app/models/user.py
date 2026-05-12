from sqlalchemy import Column, Integer, String, DateTime, func
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    picture = Column(String(500), nullable=True)
    provider = Column(String(50), default="google")
    provider_id = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")
    created_at = Column(DateTime, server_default=func.now())
