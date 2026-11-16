import numpy as np
from typing import Dict, Any, Tuple, List, Optional
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix
)
from scipy import stats

def calcular_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """
    Computes Expected Calibration Error (ECE).
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    if n == 0:
        return 0.0

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        in_bin = (y_prob > bin_lower) & (y_prob <= bin_upper) if i > 0 else (y_prob >= bin_lower) & (y_prob <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(y_true[in_bin])
            avg_confidence_in_bin = np.mean(y_prob[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return round(float(ece), 4)

def encontrar_umbral_optimo(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """
    Finds optimal decision threshold on validation set maximizing Youden's J statistic:
    J = Sensitivity + Specificity - 1
    """
    best_threshold = 0.5
    best_j = -1.0
    thresholds = np.linspace(0.1, 0.9, 81)

    for th in thresholds:
        y_pred = (y_prob >= th).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        sens = tp / (tp + fn) if (tp + fn) > 0 else 0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0
        j = sens + spec - 1.0
        if j > best_j:
            best_j = j
            best_threshold = th

    return round(float(best_threshold), 3)

def evaluar_clasificador(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: Optional[float] = None,
    weights: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Computes full scientific evaluation metric battery.
    """
    if len(y_true) == 0:
        return {}

    if threshold is None:
        threshold = 0.5

    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob, sample_weight=weights))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_prob, sample_weight=weights))
    except Exception:
        pr_auc = float(np.mean(y_true))

    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred, sample_weight=weights)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(sens), 4), # Sensitivity
        "specificity": round(float(spec), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(float(brier_score_loss(y_true, y_prob, sample_weight=weights)), 4),
        "ece_calibracion": calcular_ece(y_true, y_prob),
        "umbral_optimo": round(float(threshold), 3),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        }
    }

def bootstrap_confidence_intervals(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
    n_bootstraps: int = 1000,
    seed: int = 42
) -> Dict[str, List[float]]:
    """
    Calculates 95% empirical bootstrap confidence intervals for key metrics.
    """
    rng = np.random.RandomState(seed)
    n = len(y_true)
    aucs = []
    f1s = []
    sens_list = []
    spec_list = []
    briers = []

    for _ in range(n_bootstraps):
        idx = rng.randint(0, n, size=n)
        sample_true = y_true[idx]
        sample_prob = y_prob[idx]

        if len(np.unique(sample_true)) < 2:
            continue

        sample_pred = (sample_prob >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(sample_true, sample_pred, labels=[0, 1]).ravel()

        aucs.append(roc_auc_score(sample_true, sample_prob))
        f1s.append(f1_score(sample_true, sample_pred, zero_division=0))
        sens_list.append(tp / (tp + fn) if (tp + fn) > 0 else 0)
        spec_list.append(tn / (tn + fp) if (tn + fp) > 0 else 0)
        briers.append(brier_score_loss(sample_true, sample_prob))

    def get_ci(values):
        if not values:
            return [0.0, 0.0]
        return [round(float(np.percentile(values, 2.5)), 4), round(float(np.percentile(values, 97.5)), 4)]

    return {
        "roc_auc": get_ci(aucs),
        "f1_score": get_ci(f1s),
        "sensitivity": get_ci(sens_list),
        "specificity": get_ci(spec_list),
        "brier_score": get_ci(briers)
    }

def prueba_mcnemar(y_true: np.ndarray, y_pred_a: np.ndarray, y_pred_b: np.ndarray) -> Dict[str, Any]:
    """
    McNemar paired statistical test with continuity correction.
    b: Model A correct, Model B incorrect
    c: Model A incorrect, Model B correct
    chi2 = (|b - c| - 1)^2 / (b + c)
    """
    correct_a = (y_pred_a == y_true)
    correct_b = (y_pred_b == y_true)

    b = int(np.sum(correct_a & ~correct_b))
    c = int(np.sum(~correct_a & correct_b))
    total_discordant = b + c

    if total_discordant == 0:
        return {"chi2": 0.0, "p_value": 1.0, "b": 0, "c": 0, "diferencia_significativa": False}

    chi2 = ((abs(b - c) - 1.0) ** 2) / total_discordant
    p_value = 1.0 - stats.chi2.cdf(chi2, df=1)

    return {
        "chi2": round(float(chi2), 4),
        "p_value": round(float(p_value), 4),
        "b_solo_a_acerto": b,
        "c_solo_b_acerto": c,
        "diferencia_significativa": bool(p_value < 0.05)
    }

def prueba_wilcoxon(scores_a: List[float], scores_b: List[float]) -> Dict[str, Any]:
    """
    Wilcoxon signed-rank test for paired cross-validation folds.
    """
    if len(scores_a) < 5 or scores_a == scores_b:
        return {"statistic": 0.0, "p_value": 1.0, "diferencia_significativa": False}
    try:
        stat, p_val = stats.wilcoxon(scores_a, scores_b)
        return {
            "statistic": round(float(stat), 4),
            "p_value": round(float(p_val), 4),
            "diferencia_significativa": bool(p_val < 0.05)
        }
    except Exception:
        return {"statistic": 0.0, "p_value": 1.0, "diferencia_significativa": False}

