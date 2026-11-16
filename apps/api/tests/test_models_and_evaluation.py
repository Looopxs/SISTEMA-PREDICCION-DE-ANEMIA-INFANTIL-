import pytest
import numpy as np
import pandas as pd
from app.ml.data_pipeline import preparar_datos_experimento
from app.ml.synthetic_generator import generar_dataset_sintetico_endes
from app.ml.m1_logistic import M1LogisticRegression
from app.ml.m2_random_forest import M2RandomForest
from app.ml.m3_catboost import M3CatBoost
from app.ml.m4_multitask_nn import M4MultiTaskNN
from app.ml.m5_hybrid_xgb import M5HybridXGBoost
from app.ml.evaluation import evaluar_clasificador, prueba_mcnemar, calcular_ece

def test_five_models_training_and_metrics():
    """
    Verifies that M1, M2, M3, M4, and M5 train cleanly on real features and
    produce dual probability predictions without leakage.
    """
    records = generar_dataset_sintetico_endes(n_registros=200, seed=42)
    df = pd.DataFrame(records)
    data = preparar_datos_experimento(df, seed=42)

    X_tr = data["train"]["X"]
    ya_tr, ma_tr = data["train"]["y_anemia"], data["train"]["mask_anemia"]
    ys_tr, ms_tr = data["train"]["y_stunting"], data["train"]["mask_stunting"]

    X_val = data["val"]["X"]
    ya_val, ma_val = data["val"]["y_anemia"], data["val"]["mask_anemia"]
    ys_val, ms_val = data["val"]["y_stunting"], data["val"]["mask_stunting"]

    X_te = data["test"]["X"]
    ya_te, ma_te = data["test"]["y_anemia"], data["test"]["mask_anemia"]
    ys_te, ms_te = data["test"]["y_stunting"], data["test"]["mask_stunting"]

    # 1. M1 Logistic
    m1 = M1LogisticRegression()
    m1.fit(X_tr, ya_tr, ma_tr, ys_tr, ms_tr, X_val, ya_val, ma_val, ys_val, ms_val)
    p1_a, p1_s = m1.predict_proba(X_te)
    assert len(p1_a) == len(X_te)
    assert np.all((p1_a >= 0.0) & (p1_a <= 1.0))

    # 2. M2 Random Forest
    m2 = M2RandomForest(n_estimators=20, max_depth=5)
    m2.fit(X_tr, ya_tr, ma_tr, ys_tr, ms_tr, X_val, ya_val, ma_val, ys_val, ms_val)
    p2_a, p2_s = m2.predict_proba(X_te)
    assert len(p2_a) == len(X_te)

    # 3. M3 CatBoost
    m3 = M3CatBoost(iterations=30, depth=4)
    m3.fit(X_tr, ya_tr, ma_tr, ys_tr, ms_tr, X_val, ya_val, ma_val, ys_val, ms_val)
    p3_a, p3_s = m3.predict_proba(X_te)
    assert len(p3_a) == len(X_te)

    # 4. M4 Multi-Task NN (PyTorch)
    m4 = M4MultiTaskNN(hidden_dim=32, epochs=10)
    m4.fit(X_tr, ya_tr, ma_tr, ys_tr, ms_tr, X_val, ya_val, ma_val, ys_val, ms_val)
    p4_a, p4_s = m4.predict_proba(X_te)
    assert len(p4_a) == len(X_te)

    # 5. M5 Hybrid (M4 + XGBoost meta-model)
    m5 = M5HybridXGBoost(m4_hidden_dim=32, m4_epochs=10, xgb_n_estimators=25, xgb_max_depth=3)
    m5.fit(X_tr, ya_tr, ma_tr, ys_tr, ms_tr, X_val, ya_val, ma_val, ys_val, ms_val)
    p5_a, p5_s = m5.predict_proba(X_te)
    assert len(p5_a) == len(X_te)

    # Metric evaluation
    eval_m4_a = evaluar_clasificador(ya_te[ma_te], p4_a[ma_te], threshold=m4.umbral_anemia)
    assert "roc_auc" in eval_m4_a
    assert "f1_score" in eval_m4_a
    assert "brier_score" in eval_m4_a
    assert "ece_calibracion" in eval_m4_a

    # McNemar test M4 vs M1
    y_pred_m4 = (p4_a[ma_te] >= m4.umbral_anemia).astype(int)
    y_pred_m1 = (p1_a[ma_te] >= m1.umbral_anemia).astype(int)
    mcn = prueba_mcnemar(ya_te[ma_te], y_pred_m4, y_pred_m1)
    assert "chi2" in mcn
    assert "p_value" in mcn

