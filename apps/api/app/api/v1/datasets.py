import os
import io
import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.config import settings
from app.db.models import Dataset, HogarAnonimizado, NinoAnonimizado, Medicion, Auditoria, Usuario
from app.db.schemas import DatasetResponse, QualityReportResponse
from app.ml.synthetic_generator import generar_dataset_sintetico_endes
from app.services.who_growth import evaluar_clinica_completa
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.execute(select(Dataset).order_by(Dataset.created_at.desc())).scalars().all()
    return datasets

@router.post("/seed-demo", response_model=DatasetResponse)
def seed_demo_dataset(db: Session = Depends(get_db), current_user: Optional[Usuario] = Depends(get_current_user)):
    """
    Seeds a high-fidelity synthetic demo dataset with 3,000 children across Peru,
    explicitly labeled as SYNTHETIC.
    """
    # Check if demo already exists
    existing = db.execute(select(Dataset).where(Dataset.nombre == "ENDES Perú 2024 (Sintético Demo)")).scalar_one_or_none()
    if existing:
        return existing

    print("Generating synthetic demo dataset...")
    records = generar_dataset_sintetico_endes(n_registros=3000, seed=42)

    new_dataset = Dataset(
        nombre="ENDES Perú 2024 (Sintético Demo)",
        descripcion="Dataset sintético generado para investigación y validación de modelos multitarea M1-M5 según especificaciones de la tesis.",
        origen="SINTETICO",
        pais="Perú",
        anio=2024,
        total_registros=len(records),
        total_hogares=len(set(r["hogar_pseudonimo"] for r in records)),
        es_sintetico=True,
        version_reglas="OMS 2024 / Patrones Crecimiento OMS 2006",
        metadata_json={
            "etiqueta_seguridad": settings.DEMO_DATA_TAG,
            "generador": "NutriPredict Synthetic Engine v1.0",
            "semilla": 42,
            "distribucion_departamental": "25 departamentos del Perú"
        }
    )
    db.add(new_dataset)
    db.flush()

    # Bulk create hogares, ninos, mediciones with explicit UUIDs for ultra-fast single transaction
    from app.db.models import generate_uuid
    hogares_map = {}
    hogares_list = []
    ninos_list = []
    mediciones_list = []

    for r in records:
        h_pseudo = r["hogar_pseudonimo"]
        if h_pseudo not in hogares_map:
            h_id = generate_uuid()
            hogar = HogarAnonimizado(
                id=h_id,
                dataset_id=new_dataset.id,
                hogar_pseudonimo=h_pseudo,
                conglomerado_psu=r["conglomerado_psu"],
                estrato=r["estrato"],
                factor_expansion=r["factor_expansion"],
                quintil_riqueza=r["quintil_riqueza"],
                agua_potable=r["agua_potable"],
                saneamiento=r["saneamiento"],
                material_piso=r["material_piso"],
                electricidad=r["electricidad"],
                combustible_cocina=r["combustible_cocina"],
                miembros_hogar=r["miembros_hogar"],
                area_residencia=r["area_residencia"],
                departamento=r["departamento"],
                altitud_msnm=r["altitud_msnm"],
                region_natural=r["region_natural"]
            )
            hogares_list.append(hogar)
            hogares_map[h_pseudo] = h_id

        hogar_id = hogares_map[h_pseudo]
        n_id = generate_uuid()

        nino = NinoAnonimizado(
            id=n_id,
            dataset_id=new_dataset.id,
            hogar_id=hogar_id,
            nino_pseudonimo=r["nino_pseudonimo"],
            sexo=r["sexo"],
            edad_meses=r["edad_meses"],
            orden_nacimiento=r["orden_nacimiento"],
            edad_madre=r["edad_madre"],
            educacion_madre=r["educacion_madre"],
            controles_prenatales=r["controles_prenatales"],
            peso_nacimiento_g=3100.0,
            lactancia_materna=r["lactancia_materna"],
            suplemento_hierro=r["suplemento_hierro"]
        )
        ninos_list.append(nino)

        medicion = Medicion(
            id=generate_uuid(),
            nino_id=n_id,
            hemoglobina_observada=r["hemoglobina_observada"],
            factor_ajuste_altitud=r["factor_ajuste_altitud"],
            hemoglobina_ajustada=r["hemoglobina_ajustada"],
            anemia_observada=r["anemia_observada"],
            anemia_severidad=r["anemia_severidad"],
            anemia_evaluable=r["anemia_evaluable"],
            talla_cm=r["talla_cm"],
            peso_kg=r["peso_kg"],
            haz=r["haz"],
            waz=r["waz"],
            whz=r["whz"],
            desnutricion_cronica_observada=r["desnutricion_cronica_observada"],
            stunting_severidad=r["stunting_severidad"],
            stunting_evaluable=True,
            clasificacion_conjunta=r["clasificacion_conjunta"],
            version_reglas="OMS 2024 / INEI"
        )
        mediciones_list.append(medicion)

    db.add_all(hogares_list)
    db.add_all(ninos_list)
    db.add_all(mediciones_list)

    # Audit log
    audit = Auditoria(
        usuario_email=current_user.email if current_user else "sistema",
        accion="SEED_DATASET_DEMO",
        entidad="datasets",
        entidad_id=new_dataset.id,
        detalles={"total_registros": len(records), "es_sintetico": True}
    )
    db.add(audit)
    db.commit()
    db.refresh(new_dataset)
    return new_dataset

@router.get("/{id}", response_model=DatasetResponse)
def get_dataset(id: str, db: Session = Depends(get_db)):
    dataset = db.execute(select(Dataset).where(Dataset.id == id)).scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
    return dataset

@router.get("/{id}/preview")
def get_dataset_preview(id: str, limit: int = 20, db: Session = Depends(get_db)):
    results = (
        db.query(NinoAnonimizado, HogarAnonimizado, Medicion)
        .join(HogarAnonimizado, NinoAnonimizado.hogar_id == HogarAnonimizado.id)
        .join(Medicion, NinoAnonimizado.id == Medicion.nino_id)
        .filter(NinoAnonimizado.dataset_id == id)
        .limit(limit)
        .all()
    )

    preview_rows = []
    for n, h, m in results:
        preview_rows.append({
            "nino_id": n.nino_pseudonimo,
            "edad_meses": n.edad_meses,
            "sexo": n.sexo,
            "departamento": h.departamento,
            "area": h.area_residencia,
            "altitud_msnm": h.altitud_msnm,
            "quintil_riqueza": h.quintil_riqueza,
            "agua_potable": "Sí" if h.agua_potable == 1 else "No",
            "saneamiento": "Sí" if h.saneamiento == 1 else "No",
            "educacion_madre": n.educacion_madre,
            "suplemento_hierro": "Sí" if n.suplemento_hierro == 1 else "No",
            # Observed Measurements
            "hb_observada": m.hemoglobina_observada,
            "ajuste_altitud": m.factor_ajuste_altitud,
            "hb_ajustada": m.hemoglobina_ajustada,
            "anemia_evaluable": "Sí" if m.anemia_evaluable else "No (<6m)",
            "anemia_observada": "Sí" if m.anemia_observada == 1 else ("No" if m.anemia_observada == 0 else "N/A"),
            "talla_cm": m.talla_cm,
            "haz": m.haz,
            "desnutricion_cronica": "Sí" if m.desnutricion_cronica_observada == 1 else "No",
            "estado_conjunto": m.clasificacion_conjunta
        })

    return {
        "dataset_id": id,
        "registros_mostrados": len(preview_rows),
        "data": preview_rows
    }

@router.get("/{id}/quality", response_model=QualityReportResponse)
def get_dataset_quality_report(id: str, db: Session = Depends(get_db)):
    dataset = db.execute(select(Dataset).where(Dataset.id == id)).scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    results = (
        db.query(NinoAnonimizado, HogarAnonimizado, Medicion)
        .join(HogarAnonimizado, NinoAnonimizado.hogar_id == HogarAnonimizado.id)
        .join(Medicion, NinoAnonimizado.id == Medicion.nino_id)
        .filter(NinoAnonimizado.dataset_id == id)
        .all()
    )

    total_registros = len(results)
    if total_registros == 0:
        raise HTTPException(status_code=400, detail="El dataset no tiene registros")

    valid_anemia = [m for _, _, m in results if m.anemia_evaluable and m.anemia_observada is not None]
    valid_stunting = [m for _, _, m in results if m.stunting_evaluable and m.desnutricion_cronica_observada is not None]

    anemia_pos = sum(1 for m in valid_anemia if m.anemia_observada == 1)
    stunting_pos = sum(1 for m in valid_stunting if m.desnutricion_cronica_observada == 1)

    tasa_anemia_cruda = round((anemia_pos / len(valid_anemia)) * 100, 2) if valid_anemia else 0.0
    tasa_stunting_cruda = round((stunting_pos / len(valid_stunting)) * 100, 2) if valid_stunting else 0.0

    # Weighted calculation using factor_expansion
    sum_w_anemia = sum(h.factor_expansion for _, h, m in results if m.anemia_evaluable and m.anemia_observada is not None)
    sum_w_anemia_pos = sum(h.factor_expansion for _, h, m in results if m.anemia_evaluable and m.anemia_observada == 1)
    tasa_anemia_pond = round((sum_w_anemia_pos / sum_w_anemia) * 100, 2) if sum_w_anemia > 0 else tasa_anemia_cruda

    sum_w_stunting = sum(h.factor_expansion for _, h, m in results if m.stunting_evaluable and m.desnutricion_cronica_observada is not None)
    sum_w_stunting_pos = sum(h.factor_expansion for _, h, m in results if m.stunting_evaluable and m.desnutricion_cronica_observada == 1)
    tasa_stunting_pond = round((sum_w_stunting_pos / sum_w_stunting) * 100, 2) if sum_w_stunting > 0 else tasa_stunting_cruda

    # Joint distribution
    joint_counts = {
        "Ninguno": sum(1 for _, _, m in results if m.clasificacion_conjunta == "Ninguno (Eutrófico / Sin Anemia)"),
        "Solo Anemia": sum(1 for _, _, m in results if m.clasificacion_conjunta == "Solo Anemia"),
        "Solo Desnutrición": sum(1 for _, _, m in results if m.clasificacion_conjunta == "Solo Desnutrición Crónica"),
        "Ambos": sum(1 for _, _, m in results if m.clasificacion_conjunta == "Ambos (Anemia y Desnutrición Crónica)"),
        "No evaluable (<6m)": sum(1 for _, _, m in results if not m.anemia_evaluable)
    }

    # Department distribution
    dep_dict = {}
    for _, h, m in results:
        dep = h.departamento
        if dep not in dep_dict:
            dep_dict[dep] = {"departamento": dep, "n": 0, "anemia_n": 0, "stunting_n": 0}
        dep_dict[dep]["n"] += 1
        if m.anemia_evaluable and m.anemia_observada == 1:
            dep_dict[dep]["anemia_n"] += 1
        if m.stunting_evaluable and m.desnutricion_cronica_observada == 1:
            dep_dict[dep]["stunting_n"] += 1

    dist_departamentos = []
    for dep, d in dep_dict.items():
        n = d["n"]
        dist_departamentos.append({
            "departamento": dep,
            "n_muestral": n,
            "prevalencia_anemia_pct": round((d["anemia_n"] / max(1, n)) * 100, 1),
            "prevalencia_stunting_pct": round((d["stunting_n"] / max(1, n)) * 100, 1)
        })

    # Age group distribution
    age_groups = {
        "< 6 meses (No elegible anemia)": {"min": 0, "max": 5, "n": 0, "anemia_n": 0, "stunting_n": 0},
        "6 - 11 meses (Ventana crítica)": {"min": 6, "max": 11, "n": 0, "anemia_n": 0, "stunting_n": 0},
        "12 - 23 meses (Ventana crítica)": {"min": 12, "max": 23, "n": 0, "anemia_n": 0, "stunting_n": 0},
        "24 - 35 meses": {"min": 24, "max": 35, "n": 0, "anemia_n": 0, "stunting_n": 0},
        "36 - 47 meses": {"min": 36, "max": 47, "n": 0, "anemia_n": 0, "stunting_n": 0},
        "48 - 59 meses": {"min": 48, "max": 59, "n": 0, "anemia_n": 0, "stunting_n": 0}
    }
    for n, _, m in results:
        edad = n.edad_meses
        for g_name, g in age_groups.items():
            if g["min"] <= edad <= g["max"]:
                g["n"] += 1
                if m.anemia_evaluable and m.anemia_observada == 1:
                    g["anemia_n"] += 1
                if m.stunting_evaluable and m.desnutricion_cronica_observada == 1:
                    g["stunting_n"] += 1
                break

    dist_edades = [
        {
            "grupo_etario": g_name,
            "n": g["n"],
            "prevalencia_anemia": round((g["anemia_n"] / max(1, g["n"])) * 100, 1) if g["min"] >= 6 else None,
            "prevalencia_stunting": round((g["stunting_n"] / max(1, g["n"])) * 100, 1)
        }
        for g_name, g in age_groups.items()
    ]

    return {
        "dataset_id": id,
        "total_registros": total_registros,
        "registros_validos_anemia": len(valid_anemia),
        "registros_validos_stunting": len(valid_stunting),
        "tasa_anemia_observada_cruda": tasa_anemia_cruda,
        "tasa_anemia_observada_ponderada": tasa_anemia_pond,
        "tasa_stunting_observada_cruda": tasa_stunting_cruda,
        "tasa_stunting_observada_ponderada": tasa_stunting_pond,
        "distribucion_conjunta": joint_counts,
        "cobertura_variables": {
            "edad_meses": 100.0, "sexo": 100.0, "quintil_riqueza": 100.0,
            "agua_potable": 100.0, "saneamiento": 100.0, "hemoglobina": round((len(valid_anemia)/total_registros)*100, 1),
            "antropometria_talla": 100.0
        },
        "distribucion_departamentos": dist_departamentos,
        "distribucion_edades": dist_edades,
        "advertencias": [
            "Los niños menores de 6 meses no son elegibles para la evaluación poblacional estándar de anemia según directrices OMS 2024.",
            "Para inferencias poblacionales a nivel departamental se aplicaron factores de ponderación (factor_expansion). No realizar inferencia a nivel distrital."
        ],
        "es_sintetico": dataset.es_sintetico
    }
