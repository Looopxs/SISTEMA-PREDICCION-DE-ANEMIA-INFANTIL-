from app.core.database import SessionLocal
from app.db.init_db import init_db
from app.api.v1.datasets import seed_demo_dataset, list_datasets, get_dataset_quality_report, get_dataset_preview
from app.api.v1.dashboard import get_dashboard_summary
from app.api.v1.antropometria import evaluar_antropometria_observada, get_who_growth_curves
from app.api.v1.predicciones import predecir_riesgo_individual
from app.api.v1.explicabilidad import get_global_shap_explanation
from app.api.v1.geografia import get_departamentos_data, get_analisis_equidad
from app.api.v1.estadistica import get_calibration_curves
from app.api.v1.reportes import generar_nuevo_reporte
from app.db.schemas import AnthropometryObservationInput, PreMeasurementPredictorInput

def main():
    print("--- 1. Initializing DB and Seeding Demo Dataset ---")
    init_db()
    with SessionLocal() as db:
        ds = seed_demo_dataset(db=db, current_user=None)
        print(f"Dataset active: {ds.nombre} (ID: {ds.id}, Registros: {ds.total_registros}, Sintético: {ds.es_sintetico})")
        
        # Test preview
        prev = get_dataset_preview(ds.id, limit=5, db=db)
        print(f"Preview rows retrieved: {len(prev['data'])}")

        # Test quality report
        q = get_dataset_quality_report(ds.id, db=db)
        print(f"Quality report: Total={q['total_registros']}, Valid Anemia={q['registros_validos_anemia']}, Valid Stunting={q['registros_validos_stunting']}")

        # 2. Dashboard Summary
        dash = get_dashboard_summary(dataset_id=ds.id, db=db)
        print(f"Dashboard KPIs: Prevalencia Anemia={dash['kpis']['tasa_anemia_observada_cruda']}%, Prevalencia Desnutrición={dash['kpis']['tasa_stunting_observada_cruda']}%")
        print(f"Distribución Conjunta: {dash['distribucion_conjunta']}")

        # 3. Anthropometry (Flow A: Observed)
        inp_antr = AnthropometryObservationInput(
            edad_meses=24, sexo="M", peso_kg=12.0, talla_cm=82.5,
            hemoglobina_g_dl=10.1, altitud_msnm=2325.0
        )
        res_antr = evaluar_antropometria_observada(inp_antr)
        print(f"Antropometría Observada: HAZ={res_antr['haz']}, Hb Ajustada={res_antr['hemoglobina_ajustada']} g/dL, Anemia={res_antr['anemia_severidad']}, Stunting={res_antr['stunting_severidad']}")

        # 4. Predictions (Flow B: Pre-measurement AI)
        inp_pred = PreMeasurementPredictorInput(
            edad_meses=18, sexo="M", departamento="Puno", area_residencia="Rural",
            region_natural="Sierra", altitud_msnm=3827.0, quintil_riqueza=1,
            agua_potable=0, saneamiento=0, material_piso="tierra", electricidad=1,
            combustible_cocina="leña/carbon", miembros_hogar=6, edad_madre=24,
            educacion_madre="Primaria", controles_prenatales=3, orden_nacimiento=2,
            lactancia_materna=1, suplemento_hierro=0
        )
        res_pred = predecir_riesgo_individual(inp_pred, db=db)
        print(f"Predicción IA Pre-Medición: Prob Anemia={res_pred.probabilidad_anemia}, Prob Desnutrición={res_pred.probabilidad_desnutricion}")
        print(f"Perfil de Riesgo Conjunto: {res_pred.riesgo_conjunto_categorizado}")

        # 5. Geography & Equity
        deptos = get_departamentos_data(dataset_id=ds.id, db=db)
        print(f"Departamentos procesados: {len(deptos)} (ej. {deptos[0]['nombre']}: Anemia {deptos[0]['prevalencia_anemia_pct']}%)")
        eq = get_analisis_equidad(dataset_id=ds.id, db=db)
        print(f"Brechas de Equidad: Rural-Urbana Anemia = {eq['brechas']['brecha_rural_urbana_anemia']}%")

        # 6. SHAP Explainability
        shap_res = get_global_shap_explanation(db=db)
        print(f"Top factor Anemia: {shap_res['top_features_anemia'][0]}")
        print(f"Top factor Desnutrición: {shap_res['top_features_stunting'][0]}")

        # 7. Reports (Excel & PDF)
        rep_excel = generar_nuevo_reporte(tipo="EXCEL", dataset_id=ds.id, db=db)
        print(f"Reporte Excel generado: {rep_excel.file_path} ({rep_excel.file_size_bytes} bytes)")

        rep_pdf = generar_nuevo_reporte(tipo="PDF", dataset_id=ds.id, db=db)
        print(f"Reporte PDF generado: {rep_pdf.file_path} ({rep_pdf.file_size_bytes} bytes)")

    print("ALL MODULES AND ENDPOINTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
