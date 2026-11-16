import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.db.models import Experimento, Modelo, Metrica, Dataset, NinoAnonimizado, HogarAnonimizado, Medicion
from app.ml.data_pipeline import preparar_datos_experimento, PreMeasurementFeaturePipeline
from app.ml.m1_logistic import M1LogisticRegression
from app.ml.m2_random_forest import M2RandomForest
from app.ml.m3_catboost import M3CatBoost
from app.ml.m4_multitask_nn import M4MultiTaskNN
from app.ml.m5_hybrid_xgb import M5HybridXGBoost
from app.ml.evaluation import (
    evaluar_clasificador, bootstrap_confidence_intervals,
    prueba_mcnemar, prueba_wilcoxon
)
from app.ml.shap_explainer import NutriPredictSHAPExplainer

def ejecutar_experimento_completo(experimento_id: str, db: Session):
    """
    Executes complete 5-model scientific training and evaluation run:
    M1 (Logistic), M2 (Random Forest), M3 (CatBoost), M4 (Multi-Task NN), M5 (MTL + XGBoost).
    """
    exp = db.execute(select(Experimento).where(Experimento.id == experimento_id)).scalar_one_or_none()
    if not exp:
        return

    exp.estado = "en_progreso"
    exp.progreso_pct = 5
    exp.inicio_ts = datetime.now(timezone.utc)
    exp.logs_sanitizados += f"[{datetime.now().isoformat()}] Iniciando protocolo experimental M1-M5...\n"
    db.commit()

    try:
        # Load dataset rows
        ninos_query = (
            db.query(NinoAnonimizado, HogarAnonimizado, Medicion)
            .join(HogarAnonimizado, NinoAnonimizado.hogar_id == HogarAnonimizado.id)
            .join(Medicion, NinoAnonimizado.id == Medicion.nino_id)
            .filter(NinoAnonimizado.dataset_id == exp.dataset_id)
            .all()
        )

        rows = []
        for n, h, m in ninos_query:
            rows.append({
                "edad_meses": n.edad_meses,
                "sexo": n.sexo,
                "departamento": h.departamento,
                "area_residencia": h.area_residencia,
                "region_natural": h.region_natural,
                "altitud_msnm": h.altitud_msnm,
                "quintil_riqueza": h.quintil_riqueza,
                "agua_potable": h.agua_potable,
                "saneamiento": h.saneamiento,
                "material_piso": h.material_piso,
                "electricidad": h.electricidad,
                "combustible_cocina": h.combustible_cocina,
                "miembros_hogar": h.miembros_hogar,
                "edad_madre": n.edad_madre,
                "educacion_madre": n.educacion_madre,
                "controles_prenatales": n.controles_prenatales,
                "orden_nacimiento": n.orden_nacimiento,
                "lactancia_materna": n.lactancia_materna,
                "suplemento_hierro": n.suplemento_hierro,
                "conglomerado_psu": h.conglomerado_psu,
                "factor_expansion": h.factor_expansion,
                "anemia_observada": m.anemia_observada,
                "desnutricion_cronica_observada": m.desnutricion_cronica_observada
            })

        df = pd.DataFrame(rows)
        exp.logs_sanitizados += f"[{datetime.now().isoformat()}] Datos cargados: {len(df)} registros. Aplicando partición por conglomerados PSU...\n"
        exp.progreso_pct = 15
        db.commit()

        # Split data without leakage
        data = preparar_datos_experimento(df, seed=exp.semilla_random)
        X_train, y_tr_a, m_tr_a = data["train"]["X"], data["train"]["y_anemia"], data["train"]["mask_anemia"]
        y_tr_s, m_tr_s = data["train"]["y_stunting"], data["train"]["mask_stunting"]

        X_val, y_v_a, m_v_a = data["val"]["X"], data["val"]["y_anemia"], data["val"]["mask_anemia"]
        y_v_s, m_v_s = data["val"]["y_stunting"], data["val"]["mask_stunting"]

        X_test, y_te_a, m_te_a = data["test"]["X"], data["test"]["y_anemia"], data["test"]["mask_anemia"]
        y_te_s, m_te_s = data["test"]["y_stunting"], data["test"]["mask_stunting"]

        # Models map
        model_instances = {
            "M1": ("Logistic Regression", "Lineal Regularizado", M1LogisticRegression(random_state=exp.semilla_random)),
            "M2": ("Random Forest", "Ensamble Bagging", M2RandomForest(random_state=exp.semilla_random)),
            "M3": ("CatBoost", "Gradient Boosting Simétrico", M3CatBoost(random_state=exp.semilla_random)),
            "M4": ("Multi-Task Neural Network", "Deep Learning Multitarea", M4MultiTaskNN()),
            "M5": ("MTL + XGBoost Residual", "Híbrido Multitarea + Boosting", M5HybridXGBoost(random_state=exp.semilla_random))
        }

        test_preds = {}
        model_eval_results = {}
        best_auc_single_anemia = 0.0
        best_auc_single_stunting = 0.0

        progress_steps = {"M1": 30, "M2": 45, "M3": 60, "M4": 75, "M5": 90}

        for code, (nombre, familia, instance) in model_instances.items():
            exp.logs_sanitizados += f"[{datetime.now().isoformat()}] Entrenando {code}: {nombre}...\n"
            db.commit()

            instance.fit(
                X_train, y_tr_a, m_tr_a, y_tr_s, m_tr_s,
                X_val, y_v_a, m_v_a, y_v_s, m_v_s
            )

            # Test predictions
            prob_te_a, prob_te_s = instance.predict_proba(X_test)
            test_preds[code] = (prob_te_a, prob_te_s)

            # Metrics
            eval_a = evaluar_clasificador(y_te_a[m_te_a], prob_te_a[m_te_a], threshold=instance.umbral_anemia)
            eval_s = evaluar_clasificador(y_te_s[m_te_s], prob_te_s[m_te_s], threshold=instance.umbral_stunting)

            # Bootstrap CIs for test metrics
            ci_a = bootstrap_confidence_intervals(y_te_a[m_te_a], prob_te_a[m_te_a], threshold=instance.umbral_anemia, seed=exp.semilla_random)
            ci_s = bootstrap_confidence_intervals(y_te_s[m_te_s], prob_te_s[m_te_s], threshold=instance.umbral_stunting, seed=exp.semilla_random)

            if code in ["M1", "M2", "M3"]:
                best_auc_single_anemia = max(best_auc_single_anemia, eval_a["roc_auc"])
                best_auc_single_stunting = max(best_auc_single_stunting, eval_s["roc_auc"])

            # Save model to disk
            artifact_filename = f"{experimento_id}_{code}.joblib"
            artifact_path = os.path.join(settings.ARTIFACTS_DIR, artifact_filename)
            joblib.dump({"model": instance, "pipeline": data["pipeline"]}, artifact_path)

            # Compute SHAP
            explainer = NutriPredictSHAPExplainer(instance, data["feature_names"], X_train[:80])
            shap_summary = explainer.explain_global(X_test)

            # Model Card JSON
            model_card = {
                "codigo": code,
                "nombre": nombre,
                "proposito": "Investigación y vigilancia epidemiológica conjunta de anemia y desnutrición infantil.",
                "poblacion_objetivo": "Niños peruanos de 0 a 59 meses de edad (anemia evaluada en 6-59m).",
                "supuestos": "Covariables pre-medición sin filtración de biomarcadores.",
                "limitaciones": "Basado en diseño transversal de encuestas de hogares. Asociaciones no causales.",
                "metricas_clave": {"anemia_auc": eval_a["roc_auc"], "stunting_auc": eval_s["roc_auc"]},
                "shap_explicabilidad": shap_summary
            }

            # Create Modelo record
            mod_rec = Modelo(
                experimento_id=exp.id,
                codigo=code,
                nombre=nombre,
                familia=familia,
                tarea="multisalida" if code in ["M4", "M5"] else "individual",
                version="1.0.0",
                artefacto_path=artifact_path,
                estado_aprobacion="validado_internamente" if eval_a["roc_auc"] > 0.65 else "experimental",
                model_card_json=model_card,
                hiperparametros_json={"umbral_anemia": instance.umbral_anemia, "umbral_stunting": instance.umbral_stunting},
                metricas_resumen_json={
                    "anemia": eval_a,
                    "desnutricion": eval_s,
                    "auc_promedio": round((eval_a["roc_auc"] + eval_s["roc_auc"]) / 2, 4)
                }
            )
            db.add(mod_rec)
            db.flush()

            # Add Metrica records
            m_a = Metrica(
                modelo_id=mod_rec.id, tarea="anemia", subgrupo="General", split="test",
                accuracy=eval_a["accuracy"], precision=eval_a["precision"], recall=eval_a["recall"],
                specificity=eval_a["specificity"], f1_score=eval_a["f1_score"], roc_auc=eval_a["roc_auc"],
                pr_auc=eval_a["pr_auc"], brier_score=eval_a["brier_score"], ece_calibracion=eval_a["ece_calibracion"],
                umbral_optimo=instance.umbral_anemia, ci_json=ci_a
            )
            m_s = Metrica(
                modelo_id=mod_rec.id, tarea="desnutricion", subgrupo="General", split="test",
                accuracy=eval_s["accuracy"], precision=eval_s["precision"], recall=eval_s["recall"],
                specificity=eval_s["specificity"], f1_score=eval_s["f1_score"], roc_auc=eval_s["roc_auc"],
                pr_auc=eval_s["pr_auc"], brier_score=eval_s["brier_score"], ece_calibracion=eval_s["ece_calibracion"],
                umbral_optimo=instance.umbral_stunting, ci_json=ci_s
            )
            db.add_all([m_a, m_s])

            model_eval_results[code] = (eval_a, eval_s)
            exp.progreso_pct = progress_steps[code]
            db.commit()

        # Scientific Hypothesis Testing & Negative Transfer Check
        exp.logs_sanitizados += f"[{datetime.now().isoformat()}] Evaluando hipótesis y transferencia negativa (Negative Transfer)...\n"
        m4_auc_a = model_eval_results["M4"][0]["roc_auc"]
        m4_auc_s = model_eval_results["M4"][1]["roc_auc"]
        delta_anemia = round(m4_auc_a - best_auc_single_anemia, 4)
        delta_stunting = round(m4_auc_s - best_auc_single_stunting, 4)
        
        # McNemar Test: M4 vs best baseline (M3)
        pred_m4_a = (test_preds["M4"][0][m_te_a] >= model_instances["M4"][2].umbral_anemia).astype(int)
        pred_m3_a = (test_preds["M3"][0][m_te_a] >= model_instances["M3"][2].umbral_anemia).astype(int)
        mcnemar_anemia = prueba_mcnemar(y_te_a[m_te_a], pred_m4_a, pred_m3_a)

        # McNemar Test: M5 vs M4
        pred_m5_a = (test_preds["M5"][0][m_te_a] >= model_instances["M5"][2].umbral_anemia).astype(int)
        mcnemar_m5_vs_m4 = prueba_mcnemar(y_te_a[m_te_a], pred_m5_a, pred_m4_a)

        exp.logs_sanitizados += f"[{datetime.now().isoformat()}] Delta AUC Anemia (M4 vs Single): {delta_anemia:+.4f}\n"
        exp.logs_sanitizados += f"[{datetime.now().isoformat()}] Delta AUC Stunting (M4 vs Single): {delta_stunting:+.4f}\n"
        exp.logs_sanitizados += f"[{datetime.now().isoformat()}] Prueba McNemar M4 vs M3 (p-valor: {mcnemar_anemia['p_value']})\n"
        exp.logs_sanitizados += f"[{datetime.now().isoformat()}] Prueba McNemar M5 vs M4 (p-valor: {mcnemar_m5_vs_m4['p_value']})\n"

        # Determine best model based on balanced joint AUC
        best_code = max(model_eval_results.keys(), key=lambda c: (model_eval_results[c][0]["roc_auc"] + model_eval_results[c][1]["roc_auc"]) / 2)
        best_mod = db.execute(select(Modelo).where(Modelo.experimento_id == exp.id, Modelo.codigo == best_code)).scalar_one_or_none()
        if best_mod:
            best_mod.es_mejor_modelo = True

        exp.estado = "completado"
        exp.progreso_pct = 100
        exp.fin_ts = datetime.now(timezone.utc)
        exp.logs_sanitizados += f"[{datetime.now().isoformat()}] Experimento finalizado con éxito. Mejor modelo: {best_code}.\n"
        db.commit()

    except Exception as e:
        exp.estado = "fallido"
        exp.logs_sanitizados += f"\n[ERROR] {str(e)}\n"
        db.commit()
        raise

