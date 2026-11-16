import numpy as np
from typing import Tuple, Optional
from xgboost import XGBClassifier
from sklearn.model_selection import KFold
from app.ml.m4_multitask_nn import M4MultiTaskNN
from app.ml.evaluation import encontrar_umbral_optimo

class M5HybridXGBoost:
    """
    M5 Hybrid: Multi-Task Neural Network representation trunk + XGBoost meta-model / residual correction.
    Uses out-of-fold cross-validation on the training set to prevent leakage,
    feeding cross-task neural predictions into dedicated gradient-boosted trees.
    """
    def __init__(
        self,
        m4_hidden_dim: int = 64,
        m4_epochs: int = 35,
        xgb_n_estimators: int = 150,
        xgb_max_depth: int = 4,
        xgb_learning_rate: float = 0.05,
        random_state: int = 42
    ):
        self.m4_hidden_dim = m4_hidden_dim
        self.m4_epochs = m4_epochs
        self.xgb_n_estimators = xgb_n_estimators
        self.xgb_max_depth = xgb_max_depth
        self.xgb_learning_rate = xgb_learning_rate
        self.random_state = random_state

        # Base MTL Network trained on full train
        self.base_m4 = M4MultiTaskNN(hidden_dim=m4_hidden_dim, epochs=m4_epochs)

        # Meta-models per task
        self.meta_anemia = XGBClassifier(
            n_estimators=xgb_n_estimators, max_depth=xgb_max_depth,
            learning_rate=xgb_learning_rate, random_state=random_state,
            eval_metric="logloss"
        )
        self.meta_stunting = XGBClassifier(
            n_estimators=xgb_n_estimators, max_depth=xgb_max_depth,
            learning_rate=xgb_learning_rate, random_state=random_state,
            eval_metric="logloss"
        )

        self.umbral_anemia = 0.5
        self.umbral_stunting = 0.5

    def _build_meta_features(self, X: np.ndarray, prob_a: np.ndarray, prob_s: np.ndarray) -> np.ndarray:
        interaction = (prob_a * prob_s).reshape(-1, 1)
        return np.hstack([X, prob_a.reshape(-1, 1), prob_s.reshape(-1, 1), interaction])

    def fit(self, X_train: np.ndarray, y_train_anemia: np.ndarray, mask_train_anemia: np.ndarray,
            y_train_stunting: np.ndarray, mask_train_stunting: np.ndarray,
            X_val: np.ndarray, y_val_anemia: np.ndarray, mask_val_anemia: np.ndarray,
            y_val_stunting: np.ndarray, mask_val_stunting: np.ndarray):

        n_train = len(X_train)
        oof_prob_a = np.zeros(n_train)
        oof_prob_s = np.zeros(n_train)

        # 4-Fold cross-validation on train set for OOF meta-features
        kf = KFold(n_splits=4, shuffle=True, random_state=self.random_state)
        for tr_idx, oof_idx in kf.split(X_train):
            fold_m4 = M4MultiTaskNN(hidden_dim=self.m4_hidden_dim, epochs=self.m4_epochs)
            fold_m4.fit(
                X_train[tr_idx], y_train_anemia[tr_idx], mask_train_anemia[tr_idx],
                y_train_stunting[tr_idx], mask_train_stunting[tr_idx],
                X_train[oof_idx], y_train_anemia[oof_idx], mask_train_anemia[oof_idx],
                y_train_stunting[oof_idx], mask_train_stunting[oof_idx]
            )
            pa, ps = fold_m4.predict_proba(X_train[oof_idx])
            oof_prob_a[oof_idx] = pa
            oof_prob_s[oof_idx] = ps

        # Fit Base M4 on entire training set
        self.base_m4.fit(
            X_train, y_train_anemia, mask_train_anemia,
            y_train_stunting, mask_train_stunting,
            X_val, y_val_anemia, mask_val_anemia,
            y_val_stunting, mask_val_stunting
        )

        # Construct training meta-features
        Z_train = self._build_meta_features(X_train, oof_prob_a, oof_prob_s)

        # Fit Meta-Model Anemia
        self.meta_anemia.fit(
            Z_train[mask_train_anemia], y_train_anemia[mask_train_anemia]
        )

        # Fit Meta-Model Stunting
        self.meta_stunting.fit(
            Z_train[mask_train_stunting], y_train_stunting[mask_train_stunting]
        )

        # Tune thresholds on Validation set
        val_base_a, val_base_s = self.base_m4.predict_proba(X_val)
        Z_val = self._build_meta_features(X_val, val_base_a, val_base_s)

        prob_val_a = self.meta_anemia.predict_proba(Z_val[mask_val_anemia])[:, 1]
        self.umbral_anemia = encontrar_umbral_optimo(y_val_anemia[mask_val_anemia], prob_val_a)

        prob_val_s = self.meta_stunting.predict_proba(Z_val[mask_val_stunting])[:, 1]
        self.umbral_stunting = encontrar_umbral_optimo(y_val_stunting[mask_val_stunting], prob_val_s)

        return self

    def predict_proba(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        base_a, base_s = self.base_m4.predict_proba(X)
        Z = self._build_meta_features(X, base_a, base_s)
        prob_a = self.meta_anemia.predict_proba(Z)[:, 1]
        prob_s = self.meta_stunting.predict_proba(Z)[:, 1]
        return prob_a, prob_s

