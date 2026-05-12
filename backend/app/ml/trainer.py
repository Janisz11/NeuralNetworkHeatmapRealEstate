import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader, TensorDataset, random_split
from typing import List, Dict, Any
from sklearn.metrics import r2_score as sklearn_r2

from .model import build_model
from .preprocessing import fit_stats, normalize_dataset, FeatureStats

TRAINING_STATE: Dict[int, Dict[str, Any]] = {}


def train_model(
    run_id: int,
    df: pd.DataFrame,
    epochs: int,
    learning_rate: float,
    hidden_layers: List[int],
    weights_path: str,
    batch_size: int = 32,
    val_split: float = 0.2,
) -> Dict[str, Any]:
    TRAINING_STATE[run_id] = {
        "status": "training",
        "current_epoch": 0,
        "total_epochs": epochs,
        "loss": None,
        "r2_score": None,
        "loss_history": [],
    }

    stats = fit_stats(df)
    X, y = normalize_dataset(df, stats)

    X_tensor = torch.tensor(X)
    y_tensor = torch.tensor(y).unsqueeze(1)

    dataset = TensorDataset(X_tensor, y_tensor)
    val_size = max(1, int(len(dataset) * val_split))
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    model = build_model(hidden_layers)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, patience=20, factor=0.5, min_lr=1e-6
    )

    val_X = val_ds.dataset.tensors[0][val_ds.indices]
    val_y = val_ds.dataset.tensors[1][val_ds.indices]

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(X_batch)

        train_loss = epoch_loss / train_size

        model.eval()
        with torch.no_grad():
            val_preds = model(val_X).squeeze().numpy()
            val_true = val_y.squeeze().numpy()
            val_loss = float(nn.MSELoss()(model(val_X), val_y))
            r2 = float(sklearn_r2(val_true, val_preds))

        scheduler.step(val_loss)

        TRAINING_STATE[run_id]["current_epoch"] = epoch
        TRAINING_STATE[run_id]["loss"] = round(train_loss, 6)
        TRAINING_STATE[run_id]["r2_score"] = round(r2, 4)
        TRAINING_STATE[run_id]["loss_history"].append(round(train_loss, 6))

    os.makedirs(os.path.dirname(weights_path), exist_ok=True)
    torch.save({
        "model_state": model.state_dict(),
        "hidden_layers": hidden_layers,
        "stats": stats,
    }, weights_path)

    TRAINING_STATE[run_id]["status"] = "done"
    return {
        "mse_loss": TRAINING_STATE[run_id]["loss"],
        "r2_score": TRAINING_STATE[run_id]["r2_score"],
    }
