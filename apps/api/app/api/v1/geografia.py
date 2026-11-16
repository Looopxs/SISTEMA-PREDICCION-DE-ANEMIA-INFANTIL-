from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.db.models import NinoAnonimizado, HogarAnonimizado, Medicion, Dataset
from app.core.peru_metadata import DEPARTAMENTOS_METADATA

router = APIRouter()

@router.get("/departamentos")
def get_departamentos_data(dataset_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns geographical distribution for all 25 departments of Peru.
    Includes observed rates, sample sizes, and warning when n < 30.
    """
    # Query database
    query = (
        db.query(HogarAnonimizado.departamento, Medicion.anemia_evaluable, Medicion.anemia_observada, Medicion.stunting_evaluable, Medicion.desnutricion_cronica_observada)
        .join(NinoAnonimizado, NinoAnonimizado.hogar_id == HogarAnonimizado.id)
        .join(Medicion, NinoAnonimizado.id == Medicion.nino_id)
    )
    if dataset_id:
        query = query.filter(HogarAnonimizado.dataset_id == dataset_id)

    rows = query.all()

    # Aggregate by department
    stats_map = {}
    for dep_name, a_eval, a_obs, s_eval, s_obs in rows:
        if dep_name not in stats_map:
            stats_map[dep_name] = {"n": 0, "anemia_valid": 0, "anemia_pos": 0, "stunting_valid": 0, "stunting_pos": 0}
        stats_map[dep_name]["n"] += 1
        if a_eval and a_obs is not None:
            stats_map[dep_name]["anemia_valid"] += 1
            if a_obs == 1:
                stats_map[dep_name]["anemia_pos"] += 1
        if s_eval and s_obs is not None:
            stats_map[dep_name]["stunting_valid"] += 1
            if s_obs == 1:
                stats_map[dep_name]["stunting_pos"] += 1

    dept_results = []
    for meta in DEPARTAMENTOS_METADATA:
        nombre = meta["nombre"]
        st = stats_map.get(nombre, {"n": 0, "anemia_valid": 0, "anemia_pos": 0, "stunting_valid": 0, "stunting_pos": 0})
        n = st["n"]
        prev_anemia = round((st["anemia_pos"] / max(1, st["anemia_valid"])) * 100, 1) if st["anemia_valid"] > 0 else 0.0
        prev_stunting = round((st["stunting_pos"] / max(1, st["stunting_valid"])) * 100, 1) if st["stunting_valid"] > 0 else 0.0

        dept_results.append({
            "id": meta["id"],
            "ubigeo": meta["ubigeo"],
            "nombre": nombre,
            "region_natural": meta["region_natural"],
            "altitud_msnm": meta["altitud_capital_msnm"],
            "lat": meta["lat"],
            "lon": meta["lon"],
            "n_muestral": n,
            "muestra_insuficiente": bool(n < 30),
            "prevalencia_anemia_pct": prev_anemia,
            "prevalencia_stunting_pct": prev_stunting,
            "prioridad_sanitaria": "Muy Alta" if prev_anemia >= 50 or prev_stunting >= 20 else ("Alta" if prev_anemia >= 40 or prev_stunting >= 12 else "Moderada")
        })

    return dept_results

@router.get("/equidad")
def get_analisis_equidad(dataset_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns demographic equity gaps:
    Rural vs Urban, Male vs Female, Natural Region, Wealth Quintiles.
    """
    query = (
        db.query(
            HogarAnonimizado.area_residencia,
            HogarAnonimizado.region_natural,
            HogarAnonimizado.quintil_riqueza,
            NinoAnonimizado.sexo,
            Medicion.anemia_evaluable,
            Medicion.anemia_observada,
            Medicion.stunting_evaluable,
            Medicion.desnutricion_cronica_observada
        )
        .join(NinoAnonimizado, NinoAnonimizado.hogar_id == HogarAnonimizado.id)
        .join(Medicion, NinoAnonimizado.id == Medicion.nino_id)
    )
    if dataset_id:
        query = query.filter(HogarAnonimizado.dataset_id == dataset_id)

    rows = query.all()
    if not rows:
        return {"subgrupos": [], "brechas": {}}

    def calc_group(filter_fn):
        subset = [r for r in rows if filter_fn(r)]
        n = len(subset)
        if n == 0:
            return {"n": 0, "prev_anemia": 0.0, "prev_stunting": 0.0}
        
        a_valid = [r for r in subset if r[4] and r[5] is not None]
        s_valid = [r for r in subset if r[6] and r[7] is not None]

        p_a = round((sum(1 for r in a_valid if r[5] == 1) / max(1, len(a_valid))) * 100, 1)
        p_s = round((sum(1 for r in s_valid if r[7] == 1) / max(1, len(s_valid))) * 100, 1)
        return {"n": n, "prev_anemia": p_a, "prev_stunting": p_s}

    urban = calc_group(lambda r: r[0] == "Urbana")
    rural = calc_group(lambda r: r[0] == "Rural")
    male = calc_group(lambda r: r[3] == "M")
    female = calc_group(lambda r: r[3] == "F")
    costa = calc_group(lambda r: r[1] == "Costa")
    sierra = calc_group(lambda r: r[1] == "Sierra")
    selva = calc_group(lambda r: r[1] == "Selva")
    q1 = calc_group(lambda r: r[2] == 1)
    q5 = calc_group(lambda r: r[2] == 5)

    subgrupos = [
        {"subgrupo": "Área de Residencia", "categoria": "Rural", "n": rural["n"], "prev_anemia": rural["prev_anemia"], "prev_stunting": rural["prev_stunting"]},
        {"subgrupo": "Área de Residencia", "categoria": "Urbana", "n": urban["n"], "prev_anemia": urban["prev_anemia"], "prev_stunting": urban["prev_stunting"]},
        {"subgrupo": "Sexo del Niño", "categoria": "Masculino", "n": male["n"], "prev_anemia": male["prev_anemia"], "prev_stunting": male["prev_stunting"]},
        {"subgrupo": "Sexo del Niño", "categoria": "Femenino", "n": female["n"], "prev_anemia": female["prev_anemia"], "prev_stunting": female["prev_stunting"]},
        {"subgrupo": "Región Natural", "categoria": "Sierra", "n": sierra["n"], "prev_anemia": sierra["prev_anemia"], "prev_stunting": sierra["prev_stunting"]},
        {"subgrupo": "Región Natural", "categoria": "Selva", "n": selva["n"], "prev_anemia": selva["prev_anemia"], "prev_stunting": selva["prev_stunting"]},
        {"subgrupo": "Región Natural", "categoria": "Costa", "n": costa["n"], "prev_anemia": costa["prev_anemia"], "prev_stunting": costa["prev_stunting"]},
        {"subgrupo": "Nivel Socioeconómico", "categoria": "Quintil 1 (Muy Pobre)", "n": q1["n"], "prev_anemia": q1["prev_anemia"], "prev_stunting": q1["prev_stunting"]},
        {"subgrupo": "Nivel Socioeconómico", "categoria": "Quintil 5 (Más Rico)", "n": q5["n"], "prev_anemia": q5["prev_anemia"], "prev_stunting": q5["prev_stunting"]},
    ]

    brechas = {
        "brecha_rural_urbana_anemia": round(rural["prev_anemia"] - urban["prev_anemia"], 1),
        "brecha_rural_urbana_stunting": round(rural["prev_stunting"] - urban["prev_stunting"], 1),
        "brecha_socioeconomica_q1_q5_anemia": round(q1["prev_anemia"] - q5["prev_anemia"], 1),
        "brecha_socioeconomica_q1_q5_stunting": round(q1["prev_stunting"] - q5["prev_stunting"], 1)
    }

    return {"subgrupos": subgrupos, "brechas": brechas}
