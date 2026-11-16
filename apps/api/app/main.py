import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import SessionLocal
from app.db.init_db import init_db
from app.api.v1.auth import router as auth_router
from app.api.v1.datasets import router as datasets_router, seed_demo_dataset
from app.api.v1.antropometria import router as antropometria_router
from app.api.v1.experimentos import router as experimentos_router
from app.api.v1.modelos import router as modelos_router
from app.api.v1.predicciones import router as predicciones_router
from app.api.v1.explicabilidad import router as explicabilidad_router
from app.api.v1.geografia import router as geografia_router
from app.api.v1.estadistica import router as estadistica_router
from app.api.v1.reportes import router as reportes_router
from app.api.v1.auditoria import router as auditoria_router
from app.api.v1.dashboard import router as dashboard_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    print("[NutriPredict AI] Starting backend service...")
    init_db()
    yield
    print("[NutriPredict AI] Shutting down backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Plataforma de Inteligencia Artificial Explicable para Investigación y Vigilancia Nutricional Infantil (Anemia y Desnutrición Crónica).",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Router Registration
api_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["Autenticación y RBAC"])
app.include_router(dashboard_router, prefix=f"{api_prefix}/dashboard", tags=["Dashboard Epidemiológico"])
app.include_router(datasets_router, prefix=f"{api_prefix}/datasets", tags=["Gestión e Importación de Datasets"])
app.include_router(antropometria_router, prefix=f"{api_prefix}/antropometria", tags=["Evaluación Antropométrica y Hemoglobina (Observada)"])
app.include_router(experimentos_router, prefix=f"{api_prefix}/experimentos", tags=["Laboratorio de Entrenamiento M1-M5"])
app.include_router(modelos_router, prefix=f"{api_prefix}/modelos", tags=["Catálogo y Model Cards M1-M5"])
app.include_router(predicciones_router, prefix=f"{api_prefix}/predicciones", tags=["Inferencia de Riesgo (Pre-Medición)"])
app.include_router(explicabilidad_router, prefix=f"{api_prefix}/explicabilidad", tags=["Explicabilidad SHAP"])
app.include_router(geografia_router, prefix=f"{api_prefix}/geografia", tags=["Análisis Geográfico y Equidad"])
app.include_router(estadistica_router, prefix=f"{api_prefix}/estadistica", tags=["Laboratorio Estadístico e Incertidumbre"])
app.include_router(reportes_router, prefix=f"{api_prefix}/reportes", tags=["Generación de Reportes PDF y Excel"])
app.include_router(auditoria_router, prefix=f"{api_prefix}/auditoria", tags=["Auditoría y Trazabilidad"])

@app.get("/")
def root():
    return {
        "producto": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "estado": "Operativo",
        "docs": "/docs",
        "aviso_seguridad": settings.DEMO_DATA_TAG
    }
