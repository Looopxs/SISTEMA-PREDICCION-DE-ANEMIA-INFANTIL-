import numpy as np
from typing import Tuple
from sklearn.ensemble import RandomForestClassifier
from app.ml.evaluation import encontrar_umbral_optimo

class M2RandomForest:
    """
    M2 Baseline: Independent Random Forest models for Anemia and Stunting.
    """
    def __init__(self, n_estimators: int = 150, max_depth: int = 8, random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model_anemia = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth,
            random_state=random_state, class_weight="balanced", n_jobs=-1
        )
        self.model_stunting = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth,
            random_state=random_state, class_weight="balanced", n_jobs=-1
        )
        self.umbral_anemia = 0.5
        self.umbral_stunting = 0.5

    def fit(self, X_train: np.ndarray, y_train_anemia: np.ndarray, mask_train_anemia: np.ndarray,
            y_train_stunting: np.ndarray, mask_train_stunting: np.ndarray,
            X_val: np.ndarray, y_val_anemia: np.ndarray, mask_val_anemia: np.ndarray,
            y_val_stunting: np.ndarray, mask_val_stunting: np.ndarray):
        
        self.model_anemia.fit(X_train[mask_train_anemia], y_train_anemia[mask_train_anemia])
        prob_val_a = self.model_anemia.predict_proba(X_val[mask_val_anemia])[:, 1]
        self.umbral_anemia = encontrar_umbral_optimo(y_val_anemia[mask_val_anemia], prob_val_a)

        self.model_stunting.fit(X_train[mask_train_stunting], y_train_stunting[mask_train_stunting])
        prob_val_s = self.model_stunting.predict_proba(X_val[mask_val_stunting])[:, 1]
        self.umbral_stunting = encontrar_umbral_optimo(y_val_stunting[mask_val_stunting], prob_val_s)
        return self

    def predict_proba(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        prob_a = self.model_anemia.predict_proba(X)[:, 1]
        prob_s = self.model_stunting.predict_proba(X)[:, 1]
        return prob_a, prob_s

