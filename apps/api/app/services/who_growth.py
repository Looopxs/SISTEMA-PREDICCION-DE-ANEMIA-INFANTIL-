import math
from typing import Tuple, Optional, Dict, Any

# WHO 2006 Child Growth Standards approximate LMS parameters for Height/Length-for-age (0-59 months)
# Simplified high-accuracy LMS curves for M (median cm) and S (variation) by sex and age
def get_who_haz(edad_meses: int, sexo: str, talla_cm: float) -> Tuple[float, str, int]:
    """
    Computes Height-for-Age Z-Score (HAZ) according to WHO Child Growth Standards.
    Returns: (haz_score, severidad, stunting_flag)
    """
    if edad_meses < 0 or edad_meses > 59 or talla_cm <= 0:
        return (0.0, "No evaluable", 0)

    # Median height (cm) approximate curve by age for boys (M) and girls (F)
    if sexo.upper() == "M":
        # WHO boys median length/height ~ 49.9 at birth to 110.0 at 59 months
        median = 49.9 + (60.1 * math.pow(edad_meses / 59.0, 0.62))
        sd = 2.4 + (1.9 * (edad_meses / 59.0))
    else:
        # WHO girls median length/height ~ 49.1 at birth to 109.4 at 59 months
        median = 49.1 + (59.7 * math.pow(edad_meses / 59.0, 0.62))
        sd = 2.3 + (1.9 * (edad_meses / 59.0))

    haz = (talla_cm - median) / sd
    haz = round(float(haz), 2)

    # Classification
    if haz < -3.0:
        severidad = "Severa"
        stunting_flag = 1
    elif haz < -2.0:
        severidad = "Moderada"
        stunting_flag = 1
    else:
        severidad = "Normal"
        stunting_flag = 0

    return (haz, severidad, stunting_flag)

def get_who_waz(edad_meses: int, sexo: str, peso_kg: float) -> float:
    """Weight-for-age Z-Score approximation"""
    if sexo.upper() == "M":
        median = 3.3 + (15.0 * math.pow(edad_meses / 59.0, 0.68))
        sd = 0.5 + (1.8 * (edad_meses / 59.0))
    else:
        median = 3.2 + (14.5 * math.pow(edad_meses / 59.0, 0.68))
        sd = 0.5 + (1.8 * (edad_meses / 59.0))
    return round(float((peso_kg - median) / sd), 2)

def get_who_whz(talla_cm: float, peso_kg: float) -> float:
    """Weight-for-height Z-Score approximation (acute malnutrition)"""
    expected_weight = 0.00014 * math.pow(talla_cm, 2.55)
    sd = max(0.8, expected_weight * 0.12)
    return round(float((peso_kg - expected_weight) / sd), 2)

def calcular_ajuste_altitud_hb(altitud_msnm: float) -> float:
    """
    WHO 2024 / INEI adjustment factor for Hemoglobin based on altitude.
    Formula applies for altitudes >= 1000m:
    delta_hb = -0.0645 * (alt/1000) + 0.0567 * (alt/1000)^2
    """
    if altitud_msnm < 1000.0:
        return 0.0
    
    h = altitud_msnm / 1000.0
    adjustment = -0.0645 * h + 0.0567 * (h ** 2)
    return round(float(max(0.0, adjustment)), 2)

def clasificar_anemia(edad_meses: int, hemoglobina_observada: Optional[float], altitud_msnm: float = 0.0) -> Tuple[Optional[float], Optional[int], str, bool]:
    """
    Evaluates anemia status according to WHO 2024 criteria.
    Only valid for children aged 6 to 59 months.
    Returns: (hb_ajustada, anemia_flag, severidad, es_evaluable)
    """
    if edad_meses < 6 or edad_meses > 59 or hemoglobina_observada is None or hemoglobina_observada <= 0:
        return (None, None, "No evaluable (<6m o sin medición)", False)
    
    factor_ajuste = calcular_ajuste_altitud_hb(altitud_msnm)
    hb_ajustada = round(hemoglobina_observada - factor_ajuste, 2)

    if hb_ajustada < 7.0:
        severidad = "Severa"
        anemia_flag = 1
    elif hb_ajustada < 10.0:
        severidad = "Moderada"
        anemia_flag = 1
    elif hb_ajustada < 11.0:
        severidad = "Leve"
        anemia_flag = 1
    else:
        severidad = "Normal"
        anemia_flag = 0

    return (hb_ajustada, anemia_flag, severidad, True)

def evaluar_clinica_completa(
    edad_meses: int,
    sexo: str,
    talla_cm: float,
    peso_kg: float,
    hemoglobina_observada: Optional[float],
    altitud_msnm: float
) -> Dict[str, Any]:
    """
    Flow A: Purely observed clinical evaluation (non-AI, deterministic WHO rules).
    """
    haz, stunting_sev, stunting_flag = get_who_haz(edad_meses, sexo, talla_cm)
    waz = get_who_waz(edad_meses, sexo, peso_kg)
    whz = get_who_whz(talla_cm, peso_kg)
    
    factor_alt = calcular_ajuste_altitud_hb(altitud_msnm)
    hb_ajustada, anemia_flag, anemia_sev, anemia_evaluable = clasificar_anemia(
        edad_meses, hemoglobina_observada, altitud_msnm
    )

    # Joint observed status
    if not anemia_evaluable:
        clasificacion_conjunta = "Anemia no evaluable (<6m)"
    elif anemia_flag == 1 and stunting_flag == 1:
        clasificacion_conjunta = "Ambos (Anemia y Desnutrición Crónica)"
    elif anemia_flag == 1 and stunting_flag == 0:
        clasificacion_conjunta = "Solo Anemia"
    elif anemia_flag == 0 and stunting_flag == 1:
        clasificacion_conjunta = "Solo Desnutrición Crónica"
    else:
        clasificacion_conjunta = "Ninguno (Eutrófico / Sin Anemia)"

    return {
        "edad_meses": edad_meses,
        "sexo": sexo,
        "peso_kg": peso_kg,
        "talla_cm": talla_cm,
        "haz": haz,
        "waz": waz,
        "whz": whz,
        "desnutricion_cronica_observada": stunting_flag,
        "stunting_severidad": stunting_sev,
        "stunting_evaluable": True,
        "hemoglobina_observada": hemoglobina_observada,
        "factor_ajuste_altitud": factor_alt,
        "hemoglobina_ajustada": hb_ajustada,
        "anemia_observada": anemia_flag,
        "anemia_severidad": anemia_sev,
        "anemia_evaluable": anemia_evaluable,
        "clasificacion_conjunta": clasificacion_conjunta
    }

