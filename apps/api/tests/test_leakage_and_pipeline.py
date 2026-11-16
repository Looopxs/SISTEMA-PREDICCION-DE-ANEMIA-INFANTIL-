import pytest
import pandas as pd
import numpy as np
from app.ml.data_pipeline import PreMeasurementFeaturePipeline, FORBIDDEN_LEAKAGE_COLUMNS, APPROVED_PREDICTORS
from app.ml.synthetic_generator import generar_dataset_sintetico_endes

def test_no_data_leakage_in_features():
    """
    CRITICAL SCIENTIFIC TEST:
    Verify that hemoglobin, HAZ, observed labels or direct derivatives are NEVER
    present in the feature matrix X used for prediction.
    """
    records = generar_dataset_sintetico_endes(n_registros=50, seed=123)
    df = pd.DataFrame(records)

    pipeline = PreMeasurementFeaturePipeline()
    pipeline.fit(df)
    X = pipeline.transform(df)

    # Feature names must never contain any forbidden leakage term
    for name in pipeline.feature_names_:
        for forbidden in FORBIDDEN_LEAKAGE_COLUMNS:
            assert forbidden not in name.lower(), f"DATA LEAKAGE DETECTED! '{name}' contains forbidden '{forbidden}'"

    # Number of features must match
    assert X.shape[1] == len(pipeline.feature_names_)
    assert not np.isnan(X).any(), "Feature matrix contains NaNs"

def test_who_altitude_and_haz_calculation():
    """
    Verifies WHO altitude correction for Hemoglobin and HAZ calculation.
    """
    from app.services.who_growth import calcular_ajuste_altitud_hb, clasificar_anemia, get_who_haz

    # Altitude < 1000m has 0 adjustment
    assert calcular_ajuste_altitud_hb(500) == 0.0

    # Altitude >= 1000m: 3827m (Puno)
    # formula: -0.0645*(3.827) + 0.0567*(3.827^2) ~ -0.2468 + 0.8304 ~ 0.58 g/dL
    adj_puno = calcular_ajuste_altitud_hb(3827)
    assert adj_puno > 0.4 and adj_puno < 0.8

    # Anemia for child < 6 months is NOT evaluable
    _, _, _, evaluable = clasificar_anemia(edad_meses=3, hemoglobina_observada=10.5)
    assert evaluable is False

    # Anemia for child 12 months with 10.2 g/dL at sea level (Normal cutoff is 11.0) -> Mild anemia
    hb_adj, flag, sev, evaluable = clasificar_anemia(edad_meses=12, hemoglobina_observada=10.2, altitud_msnm=0)
    assert evaluable is True
    assert flag == 1
    assert sev == "Leve"

    # HAZ for severe stunting (Z < -3)
    haz, sev_stunt, flag_stunt = get_who_haz(edad_meses=24, sexo="M", talla_cm=72.0)
    assert flag_stunt == 1
    assert haz < -2.0

