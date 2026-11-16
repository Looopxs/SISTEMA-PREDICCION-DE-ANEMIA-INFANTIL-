from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.config import settings
from app.db.models import Dataset, NinoAnonimizado, HogarAnonimizado, Medicion, Modelo, Experimento

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(dataset_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Main epidemiological dashboard KPIs:
    Distinguishes observed epidemiological statistics from AI model risk predictions.
    """
    # Find dataset
    dataset = None
    if dataset_id:
        dataset = db.execute(select(Dataset).where(Dataset.id == dataset_id)).scalar_one_or_none()
    if not dataset:
        dataset = db.execute(select(Dataset).order_by(Dataset.created_at.desc())).scalars().first()

    if not dataset:
        return {
            "has_data": False,
            "mensaje": "No hay datasets cargados. Puede inicializar la demo sintética o importar microdatos ENDES."
        }

    # Query counts and prevalences
    results = (
        db.query(NinoAnonimizado, HogarAnonimizado, Medicion)
        .join(HogarAnonimizado, NinoAnonimizado.hogar_id == HogarAnonimizado.id)
        .join(Medicion, NinoAnonimizado.id == Medicion.nino_id)
        .filter(NinoAnonimizado.dataset_id == dataset.id)
        .all()
    )

    total_ninos = len(results)
    total_hogares = len(set(h.hogar_pseudonimo for _, h, _ in results))

    valid_anemia = [m for _, _, m in results if m.anemia_evaluable and m.anemia_observada is not None]
    valid_stunting = [m for _, _, m in results if m.stunting_evaluable and m.desnutricion_cronica_observada is not None]

    anemia_pos = sum(1 for m in valid_anemia if m.anemia_observada == 1)
    stunting_pos = sum(1 for m in valid_stunting if m.desnutricion_cronica_observada == 1)

    tasa_anemia_cruda = round((anemia_pos / max(1, len(valid_anemia))) * 100, 1)
    tasa_stunting_cruda = round((stunting_pos / max(1, len(valid_stunting))) * 100, 1)

    # Weighted using factor_expansion
    sum_w_a = sum(h.factor_expansion for _, h, m in results if m.anemia_evaluable and m.anemia_observada is not None)
    sum_w_a_pos = sum(h.factor_expansion for _, h, m in results if m.anemia_evaluable and m.anemia_observada == 1)
    tasa_anemia_pond = round((sum_w_a_pos / max(1, sum_w_a)) * 100, 1)

    sum_w_s = sum(h.factor_expansion for _, h, m in results if m.stunting_evaluable and m.desnutricion_cronica_observada is not None)
    sum_w_s_pos = sum(h.factor_expansion for _, h, m in results if m.stunting_evaluable and m.desnutricion_cronica_observada == 1)
    tasa_stunting_pond = round((sum_w_s_pos / max(1, sum_w_s)) * 100, 1)

    # Joint distribution
    joint_counts = {
        "Ninguno": sum(1 for _, _, m in results if m.clasificacion_conjunta == "Ninguno (Eutrófico / Sin Anemia)"),
        "Solo Anemia": sum(1 for _, _, m in results if m.clasificacion_conjunta == "Solo Anemia"),
        "Solo Desnutrición": sum(1 for _, _, m in results if m.clasificacion_conjunta == "Solo Desnutrición Crónica"),
        "Ambos": sum(1 for _, _, m in results if m.clasificacion_conjunta == "Ambos (Anemia y Desnutrición Crónica)"),
        "No evaluable (<6m)": sum(1 for _, _, m in results if not m.anemia_evaluable)
    }

    tasa_doble_carga = round((joint_counts["Ambos"] / max(1, total_ninos)) * 100, 1)

    # Counts of models and experiments
    total_modelos = db.execute(select(func.count(Modelo.id))).scalar() or 0
    total_experimentos = db.execute(select(func.count(Experimento.id))).scalar() or 0

    return {
        "has_data": True,
        "dataset_id": dataset.id,
        "dataset_nombre": dataset.nombre,
        "dataset_anio": dataset.anio,
        "es_sintetico": dataset.es_sintetico,
        "tag_seguridad": settings.DEMO_DATA_TAG if dataset.es_sintetico else "DATOS REALES VERIFICADOS",
        "kpis": {
            "total_ninos_muestreados": total_ninos,
            "total_hogares_muestreados": total_hogares,
            "tasa_anemia_observada_cruda": tasa_anemia_cruda,
            "tasa_anemia_observada_ponderada": tasa_anemia_pond,
            "tasa_stunting_observada_cruda": tasa_stunting_cruda,
            "tasa_stunting_observada_ponderada": tasa_stunting_pond,
            "tasa_doble_carga_malnutricion": tasa_doble_carga,
            "ninos_evaluables_anemia": len(valid_anemia),
            "ninos_evaluables_stunting": len(valid_stunting)
        },
        "distribucion_conjunta": joint_counts,
        "experimentos_totales": total_experimentos,
        "modelos_entrenados": total_modelos,
        "aviso_metodologico": "Las tasas reflejan mediciones antropométricas y de hemoglobina observadas (no predicciones). La inferencia respeta los factores de ponderación muestral."
    }

