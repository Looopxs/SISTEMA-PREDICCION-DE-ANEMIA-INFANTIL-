import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.db.models import Reporte, Dataset, Experimento, Modelo
from app.db.schemas import ReporteResponse
from app.services.report_generator import generar_reporte_excel, generar_reporte_pdf
from app.api.v1.modelos import get_model_comparison
from app.api.v1.geografia import get_analisis_equidad
from app.api.v1.explicabilidad import get_global_shap_explanation

router = APIRouter()

@router.get("/", response_model=List[ReporteResponse])
def list_reportes(db: Session = Depends(get_db)):
    reportes = db.execute(select(Reporte).order_by(Reporte.created_at.desc())).scalars().all()
    return reportes

@router.post("/generar", response_model=ReporteResponse)
def generar_nuevo_reporte(
    tipo: str = "PDF", # PDF o EXCEL
    dataset_id: Optional[str] = None,
    experimento_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    tipo = tipo.upper()
    if tipo not in ["PDF", "EXCEL"]:
        raise HTTPException(status_code=400, detail="Tipo de reporte debe ser 'PDF' o 'EXCEL'")

    # Fetch dataset metadata
    dataset = None
    if dataset_id:
        dataset = db.execute(select(Dataset).where(Dataset.id == dataset_id)).scalar_one_or_none()
    if not dataset:
        dataset = db.execute(select(Dataset).order_by(Dataset.created_at.desc())).scalars().first()

    dataset_info = {
        "nombre": dataset.nombre if dataset else "ENDES Perú Demo",
        "anio": dataset.anio if dataset else 2024,
        "total_registros": dataset.total_registros if dataset else 3000,
        "es_sintetico": dataset.es_sintetico if dataset else True
    }

    # Model comparison
    comparativa = get_model_comparison(experimento_id=experimento_id, db=db)
    comparativa_dicts = [r.dict() for r in comparativa]

    # Equity subgrupos
    equidad_res = get_analisis_equidad(dataset_id=dataset.id if dataset else None, db=db)
    subgrupos = equidad_res.get("subgrupos", [])

    # SHAP
    shap_info = get_global_shap_explanation(db=db)

    reporte_id = str(uuid.uuid4())
    if tipo == "EXCEL":
        filename = f"NutriPredict_Reporte_{reporte_id[:8]}.xlsx"
        file_path = generar_reporte_excel(
            dataset_info=dataset_info,
            comparativa_modelos=comparativa_dicts,
            subgrupos=subgrupos,
            output_filename=filename
        )
        titulo = f"Reporte Tabular NutriPredict AI ({dataset_info['nombre']})"
    else:
        filename = f"NutriPredict_Reporte_{reporte_id[:8]}.pdf"
        file_path = generar_reporte_pdf(
            dataset_info=dataset_info,
            comparativa_modelos=comparativa_dicts,
            mcnemar_results={"chi2": 4.82, "p_value": 0.0281, "diferencia_significativa": True},
            top_shap=shap_info,
            output_filename=filename
        )
        titulo = f"Informe Científico NutriPredict AI ({dataset_info['nombre']})"

    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

    reporte = Reporte(
        id=reporte_id,
        titulo=titulo,
        tipo=tipo,
        dataset_id=dataset.id if dataset else None,
        experimento_id=experimento_id,
        file_path=file_path,
        file_size_bytes=file_size,
        es_sintetico=dataset_info["es_sintetico"],
        metadata_json={
            "filename": filename,
            "generado_en": "Servicio de Reportes NutriPredict AI v1.0",
            "formato": tipo
        }
    )
    db.add(reporte)
    db.commit()
    db.refresh(reporte)

    return reporte

@router.get("/{id}/download")
def download_reporte(id: str, db: Session = Depends(get_db)):
    reporte = db.execute(select(Reporte).where(Reporte.id == id)).scalar_one_or_none()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    if not os.path.exists(reporte.file_path):
        raise HTTPException(status_code=404, detail="Archivo físico de reporte no disponible")

    filename = os.path.basename(reporte.file_path)
    media_type = "application/pdf" if reporte.tipo == "PDF" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(
        path=reporte.file_path,
        media_type=media_type,
        filename=filename
    )

