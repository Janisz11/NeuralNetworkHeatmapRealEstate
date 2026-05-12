import json
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, func
from sqlalchemy.ext.hybrid import hybrid_property
from ..database import Base


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    epochs = Column(Integer, nullable=False)
    learning_rate = Column(Float, nullable=False)
    _hidden_layers = Column("hidden_layers", Text, nullable=False, default="[64, 32]")
    mse_loss = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=True)
    weights_path = Column(String(500), nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default=func.now())

    @hybrid_property
    def hidden_layers(self) -> list[int]:
        return json.loads(self._hidden_layers)

    @hidden_layers.setter
    def hidden_layers(self, value: list[int]):
        self._hidden_layers = json.dumps(value)
