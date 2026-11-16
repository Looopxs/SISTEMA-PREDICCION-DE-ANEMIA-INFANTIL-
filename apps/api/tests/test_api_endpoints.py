import pytest
from app.core.database import SessionLocal
from app.db.init_db import init_db
from app.api.v1.datasets import seed_demo_dataset, list_datasets, get_dataset_quality_report
from app.api.v1.dashboard import get_dashboard_summary
from app.api.v1.antropometria import evaluar_antropometria_observada
from app.api.v1.predicciones import predecir_riesgo_individual
from app.api.v1.geografia import get_departamentos_data, get_analisis_equidad
from app.api.v1.reportes import generar_nuevo_reporte
from app.db.schemas import AnthropometryObservationInput, PreMeasurementPredictorInput

@pytest.fixture(scope="module")
def db_session():
    init_db()
    with SessionLocal() as db:
        seed_demo_dataset(db=db, current_user=None)
        yield db

def test_datasets_and_quality(db_session):
    datasets = list_datasets(db=db_session)
    assert len(datasets) > 0
    ds = datasets[0]
    assert ds.es_sintetico is True

    quality = get_dataset_quality_report(ds.id, db=db_session)
    assert quality["total_registros"] == 3000
    assert quality["registros_validos_anemia"] > 0
    assert quality["registros_validos_stunting"] > 0

def test_dashboard_summary(db_session):
    dash = get_dashboard_summary(db=db_session)
    assert dash["has_data"] is True
    assert "tasa_anemia_observada_cruda" in dash["kpis"]
    assert "tasa_stunting_observada_cruda" in dash["kpis"]
    assert "distribucion_conjunta" in dash

def test_flow_a_antropometria():
    inp = AnthropometryObservationInput(
        edad_meses=24, sexo="M", peso_kg=12.0, talla_cm=82.5,
        hemoglobina_g_dl=10.1, altitud_msnm=2325.0
    )
    res = evaluar_antropometria_observada(inp)
    assert res["anemia_evaluable"] is True
    assert res["anemia_observada"] == 1
    assert "haz" in res
    assert "hemoglobina_ajustada" in res

def test_flow_b_prediction(db_session):
    inp = PreMeasurementPredictorInput(
        edad_meses=18, sexo="M", departamento="Puno", area_residencia="Rural",
        region_natural="Sierra", altitud_msnm=3827.0, quintil_riqueza=1,
        agua_potable=0, saneamiento=0, material_piso="tierra", electricidad=1,
        combustible_cocina="leña/carbon", miembros_hogar=6, edad_madre=24,
        educacion_madre="Primaria", controles_prenatales=3, orden_nacimiento=2,
        lactancia_materna=1, suplemento_hierro=0
    )
    res = predecir_riesgo_individual(inp, db=db_session)
    assert res.probabilidad_anemia >= 0.0
    assert res.probabilidad_desnutricion >= 0.0
    assert res.riesgo_conjunto_categorizado != ""
    assert res.es_sintetico is True

def test_geografia_and_equidad(db_session):
    deps = get_departamentos_data(db=db_session)
    assert len(deps) == 25
    equidad = get_analisis_equidad(db=db_session)
    assert "subgrupos" in equidad
    assert "brechas" in equidad

def test_report_generation(db_session):
    rep_pdf = generar_nuevo_reporte(tipo="PDF", db=db_session)
    assert rep_pdf.tipo == "PDF"
    assert rep_pdf.file_size_bytes > 0

    rep_xls = generar_nuevo_reporte(tipo="EXCEL", db=db_session)
    assert rep_xls.tipo == "EXCEL"
    assert rep_xls.file_size_bytes > 0
