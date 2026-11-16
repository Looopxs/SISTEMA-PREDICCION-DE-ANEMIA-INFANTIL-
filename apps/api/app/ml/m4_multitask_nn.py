import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Tuple, Optional
from torch.utils.data import DataLoader, TensorDataset
from app.ml.evaluation import encontrar_umbral_optimo

class MultiTaskPyTorchNet(nn.Module):
    def __init__(self, in_features: int, hidden_dim: int = 64, dropout_rate: float = 0.25):
        super().__init__()
        # Shared Trunk
        self.shared_trunk = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate)
        )
        
        # Task 1 Head (Anemia logit)
        self.head_anemia = nn.Sequential(
            nn.Linear(hidden_dim // 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

        # Task 2 Head (Stunting logit)
        self.head_stunting = nn.Sequential(
            nn.Linear(hidden_dim // 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        shared_rep = self.shared_trunk(x)
        logit_anemia = self.head_anemia(shared_rep).squeeze(-1)
        logit_stunting = self.head_stunting(shared_rep).squeeze(-1)
        return logit_anemia, logit_stunting

class M4MultiTaskNN:
    """
    M4: Multi-Task Neural Network sharing representation layers for both childhood anemia
    and chronic stunting, handling age eligibility masks and weighted multi-task loss.
    """
    def __init__(
        self,
        hidden_dim: int = 64,
        lr: float = 0.003,
        weight_decay: float = 1e-4,
        epochs: int = 40,
        batch_size: int = 64,
        device: Optional[str] = None
    ):
        self.hidden_dim = hidden_dim
        self.lr = lr
        self.weight_decay = weight_decay
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[MultiTaskPyTorchNet] = None
        self.umbral_anemia = 0.5
        self.umbral_stunting = 0.5

    def fit(self, X_train: np.ndarray, y_train_anemia: np.ndarray, mask_train_anemia: np.ndarray,
            y_train_stunting: np.ndarray, mask_train_stunting: np.ndarray,
            X_val: np.ndarray, y_val_anemia: np.ndarray, mask_val_anemia: np.ndarray,
            y_val_stunting: np.ndarray, mask_val_stunting: np.ndarray):
        
        in_features = X_train.shape[1]
        self.model = MultiTaskPyTorchNet(in_features, self.hidden_dim).to(self.device)
        
        criterion = nn.BCEWithLogitsLoss(reduction="none")
        optimizer = optim.AdamW(self.model.parameters(), lr=self.lr, weight_decay=self.weight_decay)

        # Dataset & Loader
        t_X = torch.tensor(X_train, dtype=torch.float32)
        t_ya = torch.tensor(y_train_anemia, dtype=torch.float32)
        t_ma = torch.tensor(mask_train_anemia, dtype=torch.float32)
        t_ys = torch.tensor(y_train_stunting, dtype=torch.float32)
        t_ms = torch.tensor(mask_train_stunting, dtype=torch.float32)

        dataset = TensorDataset(t_X, t_ya, t_ma, t_ys, t_ms)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        best_val_loss = float("inf")
        best_state = None

        for epoch in range(self.epochs):
            self.model.train()
            for bx, bya, bma, bys, bms in loader:
                bx, bya, bma, bys, bms = bx.to(self.device), bya.to(self.device), bma.to(self.device), bys.to(self.device), bms.to(self.device)
                optimizer.zero_grad()
                out_a, out_s = self.model(bx)

                loss_a = (criterion(out_a, bya) * bma).sum() / (bma.sum() + 1e-6)
                loss_s = (criterion(out_s, bys) * bms).sum() / (bms.sum() + 1e-6)
                total_loss = loss_a + loss_s

                total_loss.backward()
                optimizer.step()

            # Val loss check
            self.model.eval()
            with torch.no_grad():
                vx = torch.tensor(X_val, dtype=torch.float32).to(self.device)
                v_out_a, v_out_s = self.model(vx)
                v_ya = torch.tensor(y_val_anemia, dtype=torch.float32).to(self.device)
                v_ma = torch.tensor(mask_val_anemia, dtype=torch.float32).to(self.device)
                v_ys = torch.tensor(y_val_stunting, dtype=torch.float32).to(self.device)
                v_ms = torch.tensor(mask_val_stunting, dtype=torch.float32).to(self.device)

                v_loss_a = (criterion(v_out_a, v_ya) * v_ma).sum() / (v_ma.sum() + 1e-6)
                v_loss_s = (criterion(v_out_s, v_ys) * v_ms).sum() / (v_ms.sum() + 1e-6)
                v_total = (v_loss_a + v_loss_s).item()

                if v_total < best_val_loss:
                    best_val_loss = v_total
                    best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}

        if best_state is not None:
            self.model.load_state_dict(best_state)

        # Tune thresholds on validation
        prob_val_a, prob_val_s = self.predict_proba(X_val)
        self.umbral_anemia = encontrar_umbral_optimo(y_val_anemia[mask_val_anemia], prob_val_a[mask_val_anemia])
        self.umbral_stunting = encontrar_umbral_optimo(y_val_stunting[mask_val_stunting], prob_val_s[mask_val_stunting])
        return self

    def predict_proba(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if self.model is None:
            raise ValueError("Model not fitted yet")
        self.model.eval()
        with torch.no_grad():
            tx = torch.tensor(X, dtype=torch.float32).to(self.device)
            out_a, out_s = self.model(tx)
            prob_a = torch.sigmoid(out_a).cpu().numpy()
            prob_s = torch.sigmoid(out_s).cpu().numpy()
        return prob_a, prob_s

