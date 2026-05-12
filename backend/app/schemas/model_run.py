from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TrainRequest(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=200)
    epochs: int = Field(default=200, ge=1, le=2000)
    learning_rate: float = Field(default=0.001, gt=0, lt=1)
    hidden_layers: list[int] = Field(default=[64, 32])


class TrainResponse(BaseModel):
    run_id: int
    status: str


class TrainStatusResponse(BaseModel):
    run_id: int
    status: str
    current_epoch: int
    total_epochs: int
    loss: Optional[float]
    r2_score: Optional[float]


class ModelRunRead(BaseModel):
    id: int
    name: str
    epochs: int
    learning_rate: float
    hidden_layers: list[int]
    mse_loss: Optional[float]
    r2_score: Optional[float]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
