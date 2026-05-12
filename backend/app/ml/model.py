import torch
import torch.nn as nn
from typing import List


class PricePredictor(nn.Module):

    def __init__(self, input_size: int = 5, hidden_sizes: List[int] = None, dropout: float = 0.2):
        super().__init__()
        if hidden_sizes is None:
            hidden_sizes = [64, 32]

        layers: List[nn.Module] = []
        prev_size = input_size

        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(p=dropout))
            prev_size = hidden_size

        layers.append(nn.Linear(prev_size, 1))

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


def build_model(hidden_sizes: List[int] = None) -> PricePredictor:
    return PricePredictor(input_size=5, hidden_sizes=hidden_sizes or [64, 32])
