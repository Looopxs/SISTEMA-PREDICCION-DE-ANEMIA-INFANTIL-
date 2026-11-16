import asyncio
import httpx
from app.main import app

async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/")
        print("Root Status:", r.status_code)
        print("Root Body:", r.json())

        # Test seeding demo
        r_seed = await client.post("/api/v1/datasets/seed-demo")
        print("Seed Status:", r_seed.status_code)

        # Test dashboard summary
        r_dash = await client.get("/api/v1/dashboard/summary")
        print("Dashboard Status:", r_dash.status_code)
        print("Prevalencia Anemia:", r_dash.json().get("kpis", {}).get("tasa_anemia_observada_cruda"))

        # Test single prediction
        pred_payload = {
            "edad_meses": 18,
            "sexo": "M",
            "departamento": "Puno",
            "area_residencia": "Rural",
            "region_natural": "Sierra",
            "altitud_msnm": 3827.0,
            "quintil_riqueza": 1,
            "agua_potable": 0,
            "saneamiento": 0,
            "material_piso": "tierra",
            "electricidad": 1,
            "combustible_cocina": "leña/carbon",
            "miembros_hogar": 6,
            "edad_madre": 24,
            "educacion_madre": "Primaria",
            "controles_prenatales": 3,
            "orden_nacimiento": 2,
            "lactancia_materna": 1,
            "suplemento_hierro": 0
        }
        r_pred = await client.post("/api/v1/predicciones/single", json=pred_payload)
        print("Prediction Status:", r_pred.status_code)
        print("Prediction Result:", r_pred.json().get("riesgo_conjunto_categorizado"))

        # Test Excel report generation
        r_rep = await client.post("/api/v1/reportes/generar?tipo=EXCEL")
        print("Excel Report Status:", r_rep.status_code)

        # Test PDF report generation
        r_pdf = await client.post("/api/v1/reportes/generar?tipo=PDF")
        print("PDF Report Status:", r_pdf.status_code)

if __name__ == "__main__":
    asyncio.run(main())

