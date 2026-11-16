import random
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from app.services.who_growth import evaluar_clinica_completa

# Peru departments with demographic properties
DEPARTAMENTOS_PERU = [
    {"nombre": "Amazonas", "region": "Selva", "altitud": 2335, "rural_pct": 0.58, "anemia_rate": 0.44, "stunting_rate": 0.21},
    {"nombre": "Áncash", "region": "Sierra", "altitud": 3052, "rural_pct": 0.42, "anemia_rate": 0.41, "stunting_rate": 0.18},
    {"nombre": "Apurímac", "region": "Sierra", "altitud": 2378, "rural_pct": 0.54, "anemia_rate": 0.52, "stunting_rate": 0.23},
    {"nombre": "Arequipa", "region": "Costa", "altitud": 2325, "rural_pct": 0.12, "anemia_rate": 0.34, "stunting_rate": 0.07},
    {"nombre": "Ayacucho", "region": "Sierra", "altitud": 2761, "rural_pct": 0.46, "anemia_rate": 0.50, "stunting_rate": 0.22},
    {"nombre": "Cajamarca", "region": "Sierra", "altitud": 2750, "rural_pct": 0.65, "anemia_rate": 0.38, "stunting_rate": 0.26},
    {"nombre": "Callao", "region": "Costa", "altitud": 5, "rural_pct": 0.01, "anemia_rate": 0.35, "stunting_rate": 0.06},
    {"nombre": "Cusco", "region": "Sierra", "altitud": 3399, "rural_pct": 0.44, "anemia_rate": 0.54, "stunting_rate": 0.17},
    {"nombre": "Huancavelica", "region": "Sierra", "altitud": 3676, "rural_pct": 0.68, "anemia_rate": 0.56, "stunting_rate": 0.30},
    {"nombre": "Huánuco", "region": "Sierra", "altitud": 1880, "rural_pct": 0.51, "anemia_rate": 0.46, "stunting_rate": 0.23},
    {"nombre": "Ica", "region": "Costa", "altitud": 406, "rural_pct": 0.15, "anemia_rate": 0.36, "stunting_rate": 0.08},
    {"nombre": "Junín", "region": "Sierra", "altitud": 3259, "rural_pct": 0.32, "anemia_rate": 0.49, "stunting_rate": 0.16},
    {"nombre": "La Libertad", "region": "Costa", "altitud": 34, "rural_pct": 0.23, "anemia_rate": 0.39, "stunting_rate": 0.14},
    {"nombre": "Lambayeque", "region": "Costa", "altitud": 29, "rural_pct": 0.18, "anemia_rate": 0.38, "stunting_rate": 0.11},
    {"nombre": "Lima", "region": "Costa", "altitud": 154, "rural_pct": 0.03, "anemia_rate": 0.33, "stunting_rate": 0.05},
    {"nombre": "Loreto", "region": "Selva", "altitud": 106, "rural_pct": 0.42, "anemia_rate": 0.58, "stunting_rate": 0.24},
    {"nombre": "Madre de Dios", "region": "Selva", "altitud": 183, "rural_pct": 0.28, "anemia_rate": 0.48, "stunting_rate": 0.13},
    {"nombre": "Moquegua", "region": "Costa", "altitud": 1410, "rural_pct": 0.15, "anemia_rate": 0.37, "stunting_rate": 0.06},
    {"nombre": "Pasco", "region": "Sierra", "altitud": 4330, "rural_pct": 0.43, "anemia_rate": 0.57, "stunting_rate": 0.20},
    {"nombre": "Piura", "region": "Costa", "altitud": 29, "rural_pct": 0.26, "anemia_rate": 0.41, "stunting_rate": 0.13},
    {"nombre": "Puno", "region": "Sierra", "altitud": 3827, "rural_pct": 0.52, "anemia_rate": 0.67, "stunting_rate": 0.18},
    {"nombre": "San Martín", "region": "Selva", "altitud": 282, "rural_pct": 0.35, "anemia_rate": 0.47, "stunting_rate": 0.15},
    {"nombre": "Tacna", "region": "Costa", "altitud": 562, "rural_pct": 0.10, "anemia_rate": 0.36, "stunting_rate": 0.05},
    {"nombre": "Tumbes", "region": "Costa", "altitud": 6, "rural_pct": 0.09, "anemia_rate": 0.43, "stunting_rate": 0.09},
    {"nombre": "Ucayali", "region": "Selva", "altitud": 154, "rural_pct": 0.30, "anemia_rate": 0.59, "stunting_rate": 0.22}
]

def generar_dataset_sintetico_endes(n_registros: int = 3000, seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generates realistic, scientifically coherent synthetic dataset formatted like ENDES Peru.
    Explicitly labeled as SYNTHETIC. Contains:
    - Pre-measurement covariates (independent predictors)
    - Anthropometric & Hemoglobin measurements (observed endpoints)
    - WHO standard classifications
    """
    random.seed(seed)
    np.random.seed(seed)

    registros = []
    
    # 150 sampling clusters (PSUs)
    clusters = [f"CLUSTER_{i:04d}" for i in range(1, 151)]

    for i in range(1, n_registros + 1):
        dep = random.choice(DEPARTAMENTOS_PERU)
        cluster = random.choice(clusters)
        is_rural = random.random() < dep["rural_pct"]
        area_residencia = "Rural" if is_rural else "Urbana"
        
        # Socioeconomic features
        if is_rural:
            quintil_riqueza = np.random.choice([1, 2, 3, 4, 5], p=[0.45, 0.30, 0.15, 0.08, 0.02])
            agua_potable = np.random.choice([0, 1], p=[0.35, 0.65])
            saneamiento = np.random.choice([0, 1], p=[0.48, 0.52])
            material_piso = np.random.choice(["tierra", "cemento", "parquet/madera", "otro"], p=[0.55, 0.38, 0.03, 0.04])
            electricidad = np.random.choice([0, 1], p=[0.12, 0.88])
            combustible_cocina = np.random.choice(["gas", "leña/carbon", "bosta", "otro"], p=[0.30, 0.62, 0.06, 0.02])
            educacion_madre = np.random.choice(["Sin nivel", "Primaria", "Secundaria", "Superior"], p=[0.12, 0.40, 0.40, 0.08])
        else:
            quintil_riqueza = np.random.choice([1, 2, 3, 4, 5], p=[0.08, 0.17, 0.25, 0.28, 0.22])
            agua_potable = np.random.choice([0, 1], p=[0.08, 0.92])
            saneamiento = np.random.choice([0, 1], p=[0.12, 0.88])
            material_piso = np.random.choice(["tierra", "cemento", "parquet/madera", "otro"], p=[0.10, 0.62, 0.25, 0.03])
            electricidad = np.random.choice([0, 1], p=[0.02, 0.98])
            combustible_cocina = np.random.choice(["gas", "leña/carbon", "bosta", "otro"], p=[0.88, 0.10, 0.01, 0.01])
            educacion_madre = np.random.choice(["Sin nivel", "Primaria", "Secundaria", "Superior"], p=[0.02, 0.15, 0.55, 0.28])

        # Child demographics
        edad_meses = int(np.random.uniform(0, 59.9))
        sexo = random.choice(["M", "F"])
        orden_nacimiento = int(np.random.choice([1, 2, 3, 4, 5], p=[0.40, 0.30, 0.18, 0.08, 0.04]))
        edad_madre = int(np.clip(np.random.normal(26.5, 5.5), 15, 48))
        controles_prenatales = int(np.clip(np.random.poisson(6 if not is_rural else 4), 0, 14))
        miembros_hogar = int(np.clip(np.random.poisson(4.5 if not is_rural else 5.5), 2, 14))
        lactancia_materna = 1 if edad_meses <= 6 or random.random() < 0.65 else 0
        suplemento_hierro = 1 if random.random() < 0.42 else 0

        # Sample weight (factor de expansion ENDES)
        # Typically higher in rural/smaller sample areas
        factor_expansion = round(float(np.random.lognormal(mean=5.5, sigma=0.5)), 2)

        # Generate realistic measurements based on epidemiological risk curves
        # Risk factors for anemia: low age (6-23m), low wealth, low maternal education, rural, no iron
        base_hb = 11.8 - (0.4 if sexo == "M" else 0.0)
        if edad_meses < 24:
            base_hb -= 0.6 # peak vulnerability window 6-23m
        if quintil_riqueza <= 2:
            base_hb -= 0.5
        if suplemento_hierro == 1:
            base_hb += 0.4
        if educacion_madre in ["Sin nivel", "Primaria"]:
            base_hb -= 0.3
        
        # Add altitude effect on unadjusted Hb (body produces more RBC at altitude)
        alt_factor = dep["altitud"] / 1000.0
        hb_obs_mean = base_hb + (0.55 * alt_factor if dep["altitud"] >= 1000 else 0)
        hemoglobina_observada = round(float(np.clip(np.random.normal(hb_obs_mean, 1.25), 5.5, 18.0)), 1)
        
        # Height for age (HAZ)
        # Risk factors for stunting: chronic poverty, rural, sanitation lack, low maternal education, older child (stunting accumulates)
        base_haz = -0.6
        if quintil_riqueza <= 2:
            base_haz -= 0.9
        if saneamiento == 0:
            base_haz -= 0.4
        if agua_potable == 0:
            base_haz -= 0.3
        if educacion_madre in ["Sin nivel", "Primaria"]:
            base_haz -= 0.5
        if edad_meses >= 24:
            base_haz -= 0.3 # faltering accumulates after 2 years
        if is_rural:
            base_haz -= 0.3
        
        simulated_haz = float(np.clip(np.random.normal(base_haz, 1.05), -5.0, 3.0))

        # Reconstruct approximate height (cm) from simulated HAZ
        median_height = (49.9 if sexo == "M" else 49.1) + (60.0 * math.pow(edad_meses / 59.0, 0.62))
        sd_height = 2.4 + (1.9 * (edad_meses / 59.0))
        talla_cm = round(float(median_height + (simulated_haz * sd_height)), 1)
        talla_cm = max(35.0, min(125.0, talla_cm))

        # Weight (kg)
        median_weight = (3.3 if sexo == "M" else 3.2) + (14.5 * math.pow(edad_meses / 59.0, 0.68))
        peso_kg = round(float(np.clip(np.random.normal(median_weight + (simulated_haz * 1.1), 1.6), 2.0, 32.0)), 1)

        # WHO Clinical calculations
        eval_clinica = evaluar_clinica_completa(
            edad_meses=edad_meses,
            sexo=sexo,
            talla_cm=talla_cm,
            peso_kg=peso_kg,
            hemoglobina_observada=hemoglobina_observada if edad_meses >= 6 else None,
            altitud_msnm=dep["altitud"]
        )

        reg = {
            "nino_pseudonimo": f"NINO_{i:05d}",
            "hogar_pseudonimo": f"HOGAR_{cluster}_{i%50:03d}",
            "conglomerado_psu": cluster,
            "estrato": f"ESTRATO_{dep['region']}_{area_residencia}",
            "factor_expansion": factor_expansion,
            "departamento": dep["nombre"],
            "region_natural": dep["region"],
            "altitud_msnm": float(dep["altitud"]),
            "area_residencia": area_residencia,
            "quintil_riqueza": int(quintil_riqueza),
            "agua_potable": int(agua_potable),
            "saneamiento": int(saneamiento),
            "material_piso": material_piso,
            "electricidad": int(electricidad),
            "combustible_cocina": combustible_cocina,
            "miembros_hogar": int(miembros_hogar),
            "edad_madre": int(edad_madre),
            "educacion_madre": educacion_madre,
            "controles_prenatales": int(controles_prenatales),
            "sexo": sexo,
            "edad_meses": int(edad_meses),
            "orden_nacimiento": int(orden_nacimiento),
            "lactancia_materna": int(lactancia_materna),
            "suplemento_hierro": int(suplemento_hierro),
            # Measurements & WHO outcomes (strictly separated)
            "talla_cm": float(talla_cm),
            "peso_kg": float(peso_kg),
            "haz": eval_clinica["haz"],
            "waz": eval_clinica["waz"],
            "whz": eval_clinica["whz"],
            "desnutricion_cronica_observada": eval_clinica["desnutricion_cronica_observada"],
            "stunting_severidad": eval_clinica["stunting_severidad"],
            "hemoglobina_observada": eval_clinica["hemoglobina_observada"],
            "factor_ajuste_altitud": eval_clinica["factor_ajuste_altitud"],
            "hemoglobina_ajustada": eval_clinica["hemoglobina_ajustada"],
            "anemia_observada": eval_clinica["anemia_observada"],
            "anemia_severidad": eval_clinica["anemia_severidad"],
            "anemia_evaluable": eval_clinica["anemia_evaluable"],
            "clasificacion_conjunta": eval_clinica["clasificacion_conjunta"],
            "es_sintetico": True
        }
        registros.append(reg)

    return registros

import math

