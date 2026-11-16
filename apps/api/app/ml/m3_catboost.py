import numpy as np
from typing import Tuple
from catboost import CatBoostClassifier
from app.ml.evaluation import encontrar_umbral_optimo

class M3CatBoost:
    """
    M3 Baseline: Independent CatBoost models for Anemia and Stunting.
    """
    def __init__(self, iterations: int = 250, depth: int = 6, learning_rate: float = 0.05, random_state: int = 42):
        self.iterations = iterations
        self.depth = depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.model_anemia = CatBoostClassifier(
            iterations=iterations, depth=depth, learning_rate=learning_rate,
            random_seed=random_state, verbose=False, auto_class_weights="Balanced"
        )
        self.model_stunting = CatBoostClassifier(
            iterations=iterations, depth=depth, learning_rate=learning_rate,
            random_seed=random_state, verbose=False, auto_class_weights="Balanced"
        )
        self.umbral_anemia = 0.5
        self.umbral_stunting = 0.5

    def fit(self, X_train: np.ndarray, y_train_anemia: np.ndarray, mask_train_anemia: np.ndarray,
            y_train_stunting: np.ndarray, mask_train_stunting: np.ndarray,
            X_val: np.ndarray, y_val_anemia: np.ndarray, mask_val_anemia: np.ndarray,
            y_val_stunting: np.ndarray, mask_val_stunting: np.ndarray):
        
        self.model_anemia.fit(
            X_train[mask_train_anemia], y_train_anemia[mask_train_anemia],
            eval_set=(X_val[mask_val_anemia], y_val_anemia[mask_val_anemia]),
            early_stopping_rounds=30, verbose=False
        )
        prob_val_a = self.model_anemia.predict_proba(X_val[mask_val_anemia])[:, 1]
        self.umbral_anemia = encontrar_umbral_optimo(y_val_anemia[mask_val_anemia], prob_val_a)

        self.model_stunting.fit(
            X_train[mask_train_stunting], y_train_stunting[mask_train_stunting],
            eval_set=(X_val[mask_val_stunting], y_val_stunting[mask_val_stunting]),
            early_stopping_rounds=30, verbose=False
        )
        prob_val_s = self.model_stunting.predict_proba(X_val[mask_val_stunting])[:, 1]
        self.umbral_stunting = encontrar_umbral_optimo(y_val_stunting[mask_val_stunting], prob_val_s)
        return self

    def predict_proba(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        prob_a = self.model_anemia.predict_proba(X)[:, 1]
        prob_s = self.model_stunting.predict_proba(X)[:, 1]
        return prob_a, prob_s

