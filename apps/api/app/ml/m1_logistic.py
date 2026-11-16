from typing import Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from app.ml.evaluation import evaluar_clasificador, encontrar_umbral_optimo

class M1LogisticRegression:
    """
    M1 Baseline: Independent Logistic Regression models for Anemia and Stunting.
    """
    def __init__(self, C: float = 1.0, random_state: int = 42):
        self.C = C
        self.random_state = random_state
        self.model_anemia = LogisticRegression(C=C, max_iter=1000, random_state=random_state)
        self.model_stunting = LogisticRegression(C=C, max_iter=1000, random_state=random_state)
        self.umbral_anemia = 0.5
        self.umbral_stunting = 0.5

    def fit(self, X_train: np.ndarray, y_train_anemia: np.ndarray, mask_train_anemia: np.ndarray,
            y_train_stunting: np.ndarray, mask_train_stunting: np.ndarray,
            X_val: np.ndarray, y_val_anemia: np.ndarray, mask_val_anemia: np.ndarray,
            y_val_stunting: np.ndarray, mask_val_stunting: np.ndarray):
        
        # Fit Anemia on eligible children (>= 6 months)
        self.model_anemia.fit(X_train[mask_train_anemia], y_train_anemia[mask_train_anemia])
        prob_val_a = self.model_anemia.predict_proba(X_val[mask_val_anemia])[:, 1]
        self.umbral_anemia = encontrar_umbral_optimo(y_val_anemia[mask_val_anemia], prob_val_a)

        # Fit Stunting on eligible children (valid HAZ)
        self.model_stunting.fit(X_train[mask_train_stunting], y_train_stunting[mask_train_stunting])
        prob_val_s = self.model_stunting.predict_proba(X_val[mask_val_stunting])[:, 1]
        self.umbral_stunting = encontrar_umbral_optimo(y_val_stunting[mask_val_stunting], prob_val_s)
        return self

    def predict_proba(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        prob_a = self.model_anemia.predict_proba(X)[:, 1]
        prob_s = self.model_stunting.predict_proba(X)[:, 1]
        return prob_a, prob_s
