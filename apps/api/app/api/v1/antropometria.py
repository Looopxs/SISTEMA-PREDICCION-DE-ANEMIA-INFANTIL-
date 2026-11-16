import math
from fastapi import APIRouter
from app.db.schemas import AnthropometryObservationInput, AnthropometryObservationResult
from app.services.who_growth import evaluar_clinica_completa

router = APIRouter()

@router.post("/evaluar", response_model=AnthropometryObservationResult)
def evaluar_antropometria_observada(input_data: AnthropometryObservationInput):
    """
    Flow A: Pure deterministic clinical evaluation based on official WHO standards.
    Computes HAZ, WAZ, WHZ and altitude-adjusted hemoglobin without any machine learning prediction.
    """
    res = evaluar_clinica_completa(
        edad_meses=input_data.edad_meses,
        sexo=input_data.sexo,
        talla_cm=input_data.talla_cm,
        peso_kg=input_data.peso_kg,
        hemoglobina_observada=input_data.hemoglobina_g_dl,
        altitud_msnm=input_data.altitud_msnm
    )
    return res

@router.get("/curvas-patron")
def get_who_growth_curves():
    """
    Returns reference curves (-3SD, -2SD, Median, +2SD, +3SD) for WHO 2006
    length/height-for-age standards (0 to 59 months) for both boys and girls.
    """
    meses = list(range(0, 60, 2))
    
    curvas_ninos = []
    curvas_ninas = []

    for m in meses:
        # Boys
        med_m = 49.9 + (60.1 * math.pow(m / 59.0, 0.62)) if m > 0 else 49.9
        sd_m = 2.4 + (1.9 * (m / 59.0))
        curvas_ninos.append({
            "mes": m,
            "sd_neg3": round(med_m - 3 * sd_m, 1),
            "sd_neg2": round(med_m - 2 * sd_m, 1), # Stunting cutoff
            "mediana": round(med_m, 1),
            "sd_pos2": round(med_m + 2 * sd_m, 1),
            "sd_pos3": round(med_m + 3 * sd_m, 1)
        })

        # Girls
        med_f = 49.1 + (59.7 * math.pow(m / 59.0, 0.62)) if m > 0 else 49.1
        sd_f = 2.3 + (1.9 * (m / 59.0))
        curvas_ninas.append({
            "mes": m,
            "sd_neg3": round(med_f - 3 * sd_f, 1),
            "sd_neg2": round(med_f - 2 * sd_f, 1),
            "mediana": round(med_f, 1),
            "sd_pos2": round(med_f + 2 * sd_f, 1),
            "sd_pos3": round(med_f + 3 * sd_f, 1)
        })

    return {
        "ninos": curvas_ninos,
        "ninas": curvas_ninas,
        "referencia": "Patrones de Crecimiento Infantil OMS 2006",
        "umbral_desnutricion_cronica": "-2 Desviaciones Estándar (Z < -2.0)"
    }

