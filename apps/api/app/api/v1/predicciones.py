import os
import joblib
import pandas as pd
import numpy as np
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.db.models import Modelo, Prediccion, Explicacion, Auditoria
from app.db.schemas import PreMeasurementPredictorInput, SinglePredictionResponse
from app.ml.shap_explainer import NutriPredictSHAPExplainer

router = APIRouter()

@router.post("/single", response_model=SinglePredictionResponse)
def predecir_riesgo_individual(
    input_data: PreMeasurementPredictorInput,
    modelo_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Flow B: Probabilistic pre-measurement prediction (Leakage-free).
    Uses ONLY socio-demographic, maternal, and environmental predictors measured before lab/anthropometry.
    """
    # Select active model (defaults to best available or M4 / M5)
    query = select(Modelo)
    if modelo_id:
        query = query.where(Modelo.id == modelo_id)
    else:
        query = query.order_by(Modelo.es_mejor_modelo.desc(), Modelo.created_at.desc())

    modelo = db.execute(query).scalars().first()
    
    # If no model is trained yet, return an initial baseline prior estimate
    if not modelo or not modelo.artefacto_path or not os.path.exists(modelo.artefacto_path):
        # Fallback baseline prior estimation (calibrated to Peruvian national demographics)
        base_p_anemia = 0.38
        if input_data.edad_meses < 24:
            base_p_anemia += 0.18
        if input_data.quintil_riqueza <= 2:
            base_p_anemia += 0.12
        if input_data.suplemento_hierro == 1:
            base_p_anemia -= 0.14
        prob_a = float(np.clip(base_p_anemia, 0.05, 0.95))

        base_p_stunting = 0.12
        if input_data.quintil_riqueza <= 2:
            base_p_stunting += 0.16
        if input_data.saneamiento == 0:
            base_p_stunting += 0.09
        if input_data.area_residencia == "Rural":
            base_p_stunting += 0.08
        prob_s = float(np.clip(base_p_stunting, 0.02, 0.92))

        umbral_a = 0.42
        umbral_s = 0.20
        mod_codigo = "Prior Demográfico"
        mod_nombre = "Estimador Demográfico Base ENDES"
        mod_version = "1.0-pre"
        shap_factors = {
            "factores_anemia": [
                {"caracteristica": f"edad_meses ({input_data.edad_meses}m)", "impacto_shap": +0.18 if input_data.edad_meses < 24 else -0.05, "efecto": "Aumenta riesgo estimado" if input_data.edad_meses < 24 else "Reduce riesgo"},
                {"caracteristica": "suplemento_hierro", "impacto_shap": -0.14 if input_data.suplemento_hierro == 1 else +0.10, "efecto": "Reduce riesgo estimado" if input_data.suplemento_hierro == 1 else "Aumenta riesgo"},
                {"caracteristica": f"quintil_riqueza (Q{input_data.quintil_riqueza})", "impacto_shap": +0.12 if input_data.quintil_riqueza <= 2 else -0.08, "efecto": "Aumenta riesgo" if input_data.quintil_riqueza <= 2 else "Reduce riesgo"}
            ],
            "factores_stunting": [
                {"caracteristica": f"saneamiento ({'Con red' if input_data.saneamiento == 1 else 'Sin red'})", "impacto_shap": +0.09 if input_data.saneamiento == 0 else -0.07, "efecto": "Aumenta riesgo" if input_data.saneamiento == 0 else "Reduce riesgo"},
                {"caracteristica": f"quintil_riqueza (Q{input_data.quintil_riqueza})", "impacto_shap": +0.16 if input_data.quintil_riqueza <= 2 else -0.10, "efecto": "Aumenta riesgo" if input_data.quintil_riqueza <= 2 else "Reduce riesgo"},
                {"caracteristica": f"area_residencia ({input_data.area_residencia})", "impacto_shap": +0.08 if input_data.area_residencia == 'Rural' else -0.04, "efecto": "Aumenta riesgo" if input_data.area_residencia == 'Rural' else "Reduce riesgo"}
            ]
        }
    else:
        # Load trained artifact
        artifact = joblib.load(modelo.artefacto_path)
        model_obj = artifact["model"]
        pipeline = artifact["pipeline"]

        # Transform single input row
        df_row = pd.DataFrame([input_data.dict()])
        X_vec = pipeline.transform(df_row)

        pa, ps = model_obj.predict_proba(X_vec)
        prob_a = float(pa[0])
        prob_s = float(ps[0])
        umbral_a = float(model_obj.umbral_anemia)
        umbral_s = float(model_obj.umbral_stunting)
        mod_codigo = modelo.codigo
        mod_nombre = modelo.nombre
        mod_version = modelo.version

        # SHAP explanation
        explainer = NutriPredictSHAPExplainer(model_obj, pipeline.feature_names_, X_vec)
        shap_factors = explainer.explain_instance(X_vec)

    # Risk categorization
    riesgo_anemia = "Alto" if prob_a >= umbral_a + 0.15 else ("Moderado" if prob_a >= umbral_a else "Bajo")
    riesgo_stunting = "Alto" if prob_s >= umbral_s + 0.15 else ("Moderado" if prob_s >= umbral_s else "Bajo")

    # Joint vulnerability profile
    if riesgo_anemia == "Alto" and riesgo_stunting == "Alto":
        riesgo_conjunto = "Alto Riesgo de Doble Carga (Anemia y Desnutrición Crónica)"
    elif riesgo_anemia in ["Moderado", "Alto"] and riesgo_stunting in ["Moderado", "Alto"]:
        riesgo_conjunto = "Riesgo Moderado-Alto Simultáneo"
    elif riesgo_anemia in ["Moderado", "Alto"]:
        riesgo_conjunto = "Vulnerabilidad Primaria a Anemia Infantil"
    elif riesgo_stunting in ["Moderado", "Alto"]:
        riesgo_conjunto = "Vulnerabilidad Primaria a Desnutrición Crónica (Retraso de Crecimiento)"
    else:
        riesgo_conjunto = "Bajo Riesgo Estimado Simultáneo"

    # Persist prediction record
    pred = Prediccion(
        modelo_id=modelo.id if modelo else None,
        input_covariables_json=input_data.dict(),
        prob_anemia=round(prob_a, 4),
        prob_desnutricion=round(prob_s, 4),
        riesgo_anemia=riesgo_anemia,
        riesgo_desnutricion=riesgo_stunting,
        riesgo_conjunto=riesgo_conjunto,
        es_sintetico=True,
        procedencia="individual"
    )
    db.add(pred)
    db.commit()

    return SinglePredictionResponse(
        tipo_flujo="PREDICCION_PROBABILISTICA_IA",
        modelo_id=modelo.id if modelo else None,
        modelo_codigo=mod_codigo,
        modelo_nombre=mod_nombre,
        modelo_version=mod_version,
        probabilidad_anemia=round(prob_a, 4),
        riesgo_anemia=riesgo_anemia,
        umbral_decision_anemia=round(umbral_a, 3),
        probabilidad_desnutricion=round(prob_s, 4),
        riesgo_desnutricion=riesgo_stunting,
        umbral_decision_desnutricion=round(umbral_s, 3),
        riesgo_conjunto_categorizado=riesgo_conjunto,
        es_sintetico=True,
        advertencia_cientifica="Herramienta de investigación y apoyo a vigilancia nutricional. NO sustituye la valoración clínica ni emite diagnóstico médico automático.",
        explicacion_shap=shap_factors
    )

