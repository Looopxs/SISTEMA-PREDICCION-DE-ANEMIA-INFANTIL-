from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.db.models import Modelo, Metrica, Experimento
from app.db.schemas import ModeloDetailResponse, ModelComparisonRow

router = APIRouter()

@router.get("/", response_model=List[ModeloDetailResponse])
def list_modelos(db: Session = Depends(get_db)):
    modelos = db.execute(select(Modelo).order_by(Modelo.created_at.desc())).scalars().all()
    return modelos

@router.get("/comparativa", response_model=List[ModelComparisonRow])
def get_model_comparison(experimento_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns comparative table of M1 to M5 architectures across both outcomes.
    Includes negative transfer check (M4/M5 vs best single task).
    """
    query = select(Modelo)
    if experimento_id:
        query = query.where(Modelo.experimento_id == experimento_id)
    else:
        # Pick latest completed experiment if none specified
        latest_exp = db.execute(
            select(Experimento)
            .where(Experimento.estado == "completado")
            .order_by(Experimento.fin_ts.desc())
        ).scalars().first()
        if latest_exp:
            query = query.where(Modelo.experimento_id == latest_exp.id)

    modelos = db.execute(query).scalars().all()
    if not modelos:
        return []

    # Map by code
    mod_dict = {m.codigo: m for m in modelos}
    best_single_auc_anemia = max(
        [m.metricas_resumen_json.get("anemia", {}).get("roc_auc", 0.0) for c, m in mod_dict.items() if c in ["M1", "M2", "M3"]] or [0.5]
    )
    best_single_auc_stunting = max(
        [m.metricas_resumen_json.get("desnutricion", {}).get("roc_auc", 0.0) for c, m in mod_dict.items() if c in ["M1", "M2", "M3"]] or [0.5]
    )

    rows = []
    # Standard presentation order M1 to M5
    for code in ["M1", "M2", "M3", "M4", "M5"]:
        if code in mod_dict:
            m = mod_dict[code]
            res = m.metricas_resumen_json or {}
            anemia_eval = res.get("anemia", {})
            stunting_eval = res.get("desnutricion", {})

            auc_a = anemia_eval.get("roc_auc", 0.5)
            auc_s = stunting_eval.get("roc_auc", 0.5)

            # Check negative transfer
            neg_transfer = False
            if code in ["M4", "M5"]:
                if (auc_a < best_single_auc_anemia - 0.015) or (auc_s < best_single_auc_stunting - 0.015):
                    neg_transfer = True

            rows.append(ModelComparisonRow(
                codigo=m.codigo,
                nombre=m.nombre,
                familia=m.familia,
                tarea=m.tarea,
                anemia_auc=auc_a,
                anemia_pr_auc=anemia_eval.get("pr_auc", 0.5),
                anemia_f1=anemia_eval.get("f1_score", 0.0),
                anemia_sensitivity=anemia_eval.get("recall", 0.0),
                anemia_specificity=anemia_eval.get("specificity", 0.0),
                anemia_brier=anemia_eval.get("brier_score", 0.25),
                anemia_ece=anemia_eval.get("ece_calibracion", 0.05),
                stunting_auc=auc_s,
                stunting_pr_auc=stunting_eval.get("pr_auc", 0.5),
                stunting_f1=stunting_eval.get("f1_score", 0.0),
                stunting_sensitivity=stunting_eval.get("recall", 0.0),
                stunting_specificity=stunting_eval.get("specificity", 0.0),
                stunting_brier=stunting_eval.get("brier_score", 0.25),
                stunting_ece=stunting_eval.get("ece_calibracion", 0.05),
                auc_promedio=round((auc_a + auc_s) / 2, 4),
                negative_transfer_detectado=neg_transfer,
                estado_aprobacion=m.estado_aprobacion
            ))

    return rows

@router.get("/{id}", response_model=ModeloDetailResponse)
def get_modelo(id: str, db: Session = Depends(get_db)):
    modelo = db.execute(select(Modelo).where(Modelo.id == id)).scalar_one_or_none()
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return modelo

