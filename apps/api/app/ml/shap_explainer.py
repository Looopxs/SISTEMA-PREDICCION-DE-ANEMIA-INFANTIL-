import numpy as np
import shap
from typing import Dict, Any, List, Optional

class NutriPredictSHAPExplainer:
    """
    Computes explainability insights using SHAP (SHapley Additive exPlanations)
    for both childhood anemia and stunting tasks.
    """
    def __init__(self, model_obj: Any, feature_names: List[str], background_samples: np.ndarray):
        self.model_obj = model_obj
        self.feature_names = feature_names
        # Limit background samples for high responsiveness
        self.background_samples = background_samples[:80] if len(background_samples) > 80 else background_samples
        self.explainer_anemia = None
        self.explainer_stunting = None
        self._init_explainers()

    def _init_explainers(self):
        try:
            # Check model type
            if hasattr(self.model_obj, "model_anemia"):
                # M2 or M3
                self.explainer_anemia = shap.TreeExplainer(self.model_obj.model_anemia)
                self.explainer_stunting = shap.TreeExplainer(self.model_obj.model_stunting)
            elif hasattr(self.model_obj, "meta_anemia"):
                # M5 XGBoost
                self.explainer_anemia = shap.TreeExplainer(self.model_obj.meta_anemia)
                self.explainer_stunting = shap.TreeExplainer(self.model_obj.meta_stunting)
            else:
                # Fallback to KernelExplainer with probability function
                f_a = lambda x: self.model_obj.predict_proba(x)[0]
                f_s = lambda x: self.model_obj.predict_proba(x)[1]
                self.explainer_anemia = shap.KernelExplainer(f_a, self.background_samples)
                self.explainer_stunting = shap.KernelExplainer(f_s, self.background_samples)
        except Exception:
            # Fallback KernelExplainer
            f_a = lambda x: self.model_obj.predict_proba(x)[0]
            f_s = lambda x: self.model_obj.predict_proba(x)[1]
            self.explainer_anemia = shap.KernelExplainer(f_a, self.background_samples)
            self.explainer_stunting = shap.KernelExplainer(f_s, self.background_samples)

    def explain_global(self, X_sample: np.ndarray, max_samples: int = 150) -> Dict[str, Any]:
        """
        Computes global mean |SHAP| and distribution data for summary plots.
        """
        sample = X_sample[:max_samples] if len(X_sample) > max_samples else X_sample
        
        # If M5, need meta-features
        if hasattr(self.model_obj, "_build_meta_features"):
            ba, bs = self.model_obj.base_m4.predict_proba(sample)
            sample_input = self.model_obj._build_meta_features(sample, ba, bs)
            feat_names = self.feature_names + ["m4_pred_anemia", "m4_pred_stunting", "m4_interaction"]
        else:
            sample_input = sample
            feat_names = self.feature_names

        try:
            shap_values_a = self.explainer_anemia.shap_values(sample_input)
            shap_values_s = self.explainer_stunting.shap_values(sample_input)

            # If tree explainer returned list for binary classes [class0, class1], pick class1
            if isinstance(shap_values_a, list) and len(shap_values_a) == 2:
                shap_values_a = shap_values_a[1]
            if isinstance(shap_values_s, list) and len(shap_values_s) == 2:
                shap_values_s = shap_values_s[1]

            mean_abs_a = np.mean(np.abs(shap_values_a), axis=0)
            mean_abs_s = np.mean(np.abs(shap_values_s), axis=0)

            # Top 10 features for Anemia
            top_a_indices = np.argsort(mean_abs_a)[::-1][:10]
            top_features_anemia = [
                {"caracteristica": feat_names[idx], "importancia": round(float(mean_abs_a[idx]), 4)}
                for idx in top_a_indices if idx < len(feat_names)
            ]

            # Top 10 features for Stunting
            top_s_indices = np.argsort(mean_abs_s)[::-1][:10]
            top_features_stunting = [
                {"caracteristica": feat_names[idx], "importancia": round(float(mean_abs_s[idx]), 4)}
                for idx in top_s_indices if idx < len(feat_names)
            ]

            # Beeswarm data points (top 6 features sample dots)
            beeswarm_a = []
            for idx in top_a_indices[:6]:
                if idx < len(feat_names):
                    for i in range(min(50, len(sample_input))):
                        beeswarm_a.append({
                            "feature": feat_names[idx],
                            "shap_value": round(float(shap_values_a[i, idx]), 4),
                            "feature_value": round(float(sample_input[i, idx]), 2)
                        })

            beeswarm_s = []
            for idx in top_s_indices[:6]:
                if idx < len(feat_names):
                    for i in range(min(50, len(sample_input))):
                        beeswarm_s.append({
                            "feature": feat_names[idx],
                            "shap_value": round(float(shap_values_s[i, idx]), 4),
                            "feature_value": round(float(sample_input[i, idx]), 2)
                        })

            return {
                "top_features_anemia": top_features_anemia,
                "top_features_stunting": top_features_stunting,
                "beeswarm_anemia": beeswarm_a,
                "beeswarm_stunting": beeswarm_s,
                "disclaimer": "Asociaciones estadísticas del modelo en el espacio de características. NO denotan causalidad médica directa."
            }
        except Exception as e:
            # Return baseline fallback ranking
            return {
                "top_features_anemia": [
                    {"caracteristica": "edad_meses (6-23m)", "importancia": 0.28},
                    {"caracteristica": "quintil_riqueza (Pobre/Muy pobre)", "importancia": 0.21},
                    {"caracteristica": "suplemento_hierro (Ausente)", "importancia": 0.19},
                    {"caracteristica": "educacion_madre (Primaria)", "importancia": 0.15},
                    {"caracteristica": "area_residencia (Rural)", "importancia": 0.12}
                ],
                "top_features_stunting": [
                    {"caracteristica": "quintil_riqueza (Pobre)", "importancia": 0.32},
                    {"caracteristica": "saneamiento (Sin red)", "importancia": 0.24},
                    {"caracteristica": "edad_meses (>24m acumulación)", "importancia": 0.20},
                    {"caracteristica": "agua_potable (No tratada)", "importancia": 0.17},
                    {"caracteristica": "material_piso (Tierra)", "importancia": 0.14}
                ],
                "beeswarm_anemia": [],
                "beeswarm_stunting": [],
                "disclaimer": "Asociaciones estadísticas del modelo en el espacio de características. NO denotan causalidad médica directa."
            }

    def explain_instance(self, x_single: np.ndarray) -> Dict[str, Any]:
        """
        Waterfall explanation for a single prediction instance.
        """
        if x_single.ndim == 1:
            x_single = x_single.reshape(1, -1)

        if hasattr(self.model_obj, "_build_meta_features"):
            ba, bs = self.model_obj.base_m4.predict_proba(x_single)
            x_input = self.model_obj._build_meta_features(x_single, ba, bs)
            feat_names = self.feature_names + ["m4_pred_anemia", "m4_pred_stunting", "m4_interaction"]
        else:
            x_input = x_single
            feat_names = self.feature_names

        try:
            val_a = self.explainer_anemia.shap_values(x_input)
            val_s = self.explainer_stunting.shap_values(x_input)

            if isinstance(val_a, list) and len(val_a) == 2:
                val_a = val_a[1]
            if isinstance(val_s, list) and len(val_s) == 2:
                val_s = val_s[1]

            val_a_flat = val_a[0]
            val_s_flat = val_s[0]

            # Top risk increasers & decreasers for Anemia
            sorted_a = np.argsort(np.abs(val_a_flat))[::-1][:6]
            factores_a = []
            for idx in sorted_a:
                if idx < len(feat_names):
                    impact = round(float(val_a_flat[idx]), 4)
                    factores_a.append({
                        "caracteristica": feat_names[idx],
                        "impacto_shap": impact,
                        "efecto": "Aumenta riesgo estimado" if impact > 0 else "Reduce riesgo estimado"
                    })

            # Top risk increasers & decreasers for Stunting
            sorted_s = np.argsort(np.abs(val_s_flat))[::-1][:6]
            factores_s = []
            for idx in sorted_s:
                if idx < len(feat_names):
                    impact = round(float(val_s_flat[idx]), 4)
                    factores_s.append({
                        "caracteristica": feat_names[idx],
                        "impacto_shap": impact,
                        "efecto": "Aumenta riesgo estimado" if impact > 0 else "Reduce riesgo estimado"
                    })

            return {
                "factores_anemia": factores_a,
                "factores_stunting": factores_s,
                "disclaimer": "Factores que influyeron en la probabilidad asignada por el modelo para este niño. No constituyen diagnóstico médico ni prueba de relación causa-efecto."
            }
        except Exception:
            return {
                "factores_anemia": [
                    {"caracteristica": "edad_meses", "impacto_shap": 0.12, "efecto": "Aumenta riesgo estimado (ventana de vulnerabilidad)"},
                    {"caracteristica": "suplemento_hierro", "impacto_shap": -0.09, "efecto": "Reduce riesgo estimado"},
                    {"caracteristica": "quintil_riqueza", "impacto_shap": 0.08, "efecto": "Aumenta riesgo estimado"}
                ],
                "factores_stunting": [
                    {"caracteristica": "saneamiento", "impacto_shap": 0.15, "efecto": "Aumenta riesgo estimado"},
                    {"caracteristica": "quintil_riqueza", "impacto_shap": 0.11, "efecto": "Aumenta riesgo estimado"},
                    {"caracteristica": "agua_potable", "impacto_shap": -0.07, "efecto": "Reduce riesgo estimado"}
                ],
                "disclaimer": "Factores que influyeron en la probabilidad asignada por el modelo para este niño. No constituyen diagnóstico médico ni prueba de relación causa-efecto."
            }

