from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# --- Auth & User Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    nombre: str
    rol: str = "investigador"

class UserResponse(BaseModel):
    id: str
    email: str
    nombre: str
    rol: str
    activo: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Dataset Schemas ---
class DatasetCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    origen: str = "ENDES" # ENDES, DHS, SINTETICO
    anio: int = 2024
    pais: str = "Perú"
    es_sintetico: bool = False

class DatasetResponse(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None
    origen: str
    pais: str
    anio: int
    total_registros: int
    total_hogares: int
    es_sintetico: bool
    version_reglas: str
    calidad_resumen_json: Optional[Dict[str, Any]] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class QualityReportResponse(BaseModel):
    dataset_id: str
    total_registros: int
    registros_validos_anemia: int
    registros_validos_stunting: int
    tasa_anemia_observada_cruda: float
    tasa_anemia_observada_ponderada: float
    tasa_stunting_observada_cruda: float
    tasa_stunting_observada_ponderada: float
    distribucion_conjunta: Dict[str, int]
    cobertura_variables: Dict[str, float]
    distribucion_departamentos: List[Dict[str, Any]]
    distribucion_edades: List[Dict[str, Any]]
    advertencias: List[str]
    es_sintetico: bool

# --- Anthropometry & Clinical Calculation Schemas ---
class AnthropometryObservationInput(BaseModel):
    edad_meses: int = Field(..., ge=0, le=59)
    sexo: str = Field(..., pattern="^(M|F)$")
    peso_kg: float = Field(..., gt=1.0, lt=40.0)
    talla_cm: float = Field(..., gt=30.0, lt=130.0)
    hemoglobina_g_dl: Optional[float] = Field(None, gt=2.0, lt=25.0)
    altitud_msnm: float = Field(0.0, ge=0.0, le=5500.0)

class AnthropometryObservationResult(BaseModel):
    tipo_flujo: str = "EVALUACION_OBSERVADA_CLINICA"
    edad_meses: int
    sexo: str
    peso_kg: float
    talla_cm: float
    haz: float
    waz: float
    whz: float
    desnutricion_cronica_observada: int
    stunting_severidad: str
    hemoglobina_observada: Optional[float]
    factor_ajuste_altitud: float
    hemoglobina_ajustada: Optional[float]
    anemia_observada: Optional[int]
    anemia_severidad: str
    clasificacion_conjunta: str
    anemia_evaluable: bool
    stunting_evaluable: bool
    nota_metodologica: str = "Reglas estándar OMS 2024 / Patrones Crecimiento OMS 2006. Cálculo determinístico no probabilístico."

# --- Pre-Measurement Prediction Schemas (Leakage-Free) ---
class PreMeasurementPredictorInput(BaseModel):
    edad_meses: int = Field(..., ge=0, le=59, description="Edad del niño en meses (0-59)")
    sexo: str = Field(..., pattern="^(M|F)$", description="Sexo biológico (M: Masculino, F: Femenino)")
    departamento: str = Field("Lima", description="Departamento del Perú")
    area_residencia: str = Field("Urbana", pattern="^(Urbana|Rural)$")
    region_natural: str = Field("Costa", pattern="^(Costa|Sierra|Selva)$")
    altitud_msnm: float = Field(150.0, ge=0, le=5200)
    quintil_riqueza: int = Field(3, ge=1, le=5, description="1=Más pobre, 5=Más rico")
    agua_potable: int = Field(1, ge=0, le=1, description="1=Acceso a agua de red pública o protegida, 0=No")
    saneamiento: int = Field(1, ge=0, le=1, description="1=Red de alcantarillado o letrina mejorada, 0=No")
    material_piso: str = Field("cemento", description="tierra, cemento, parquet/madera, otro")
    electricidad: int = Field(1, ge=0, le=1)
    combustible_cocina: str = Field("gas", description="gas, leña/carbon, bosta, otro")
    miembros_hogar: int = Field(4, ge=1, le=20)
    edad_madre: int = Field(26, ge=12, le=55)
    educacion_madre: str = Field("Secundaria", description="Sin nivel, Primaria, Secundaria, Superior")
    controles_prenatales: int = Field(6, ge=0, le=20)
    orden_nacimiento: int = Field(1, ge=1, le=15)
    lactancia_materna: int = Field(1, ge=0, le=1)
    suplemento_hierro: int = Field(0, ge=0, le=1)

class SinglePredictionResponse(BaseModel):
    tipo_flujo: str = "PREDICCION_PROBABILISTICA_IA"
    modelo_id: Optional[str] = None
    modelo_codigo: str = "M4"
    modelo_nombre: str = "Multi-Task Neural Network"
    modelo_version: str = "1.0.0"
    probabilidad_anemia: float
    riesgo_anemia: str # Bajo, Moderado, Alto
    umbral_decision_anemia: float
    probabilidad_desnutricion: float
    riesgo_desnutricion: str
    umbral_decision_desnutricion: float
    riesgo_conjunto_categorizado: str
    es_sintetico: bool
    advertencia_cientifica: str = "Herramienta de investigación y apoyo a vigilancia nutricional. NO sustituye la valoración clínica ni emite diagnóstico médico automático."
    explicacion_shap: Optional[Dict[str, Any]] = None

# --- Experiment & Training Schemas ---
class ExperimentoCreate(BaseModel):
    dataset_id: str
    nombre: str
    descripcion: Optional[str] = None
    semilla_random: int = 42
    particion_tipo: str = "Estratificada por Conglomerados"
    train_pct: float = 0.70
    val_pct: float = 0.15
    test_pct: float = 0.15
    modelos_a_entrenar: List[str] = ["M1", "M2", "M3", "M4", "M5"]

class ExperimentoResponse(BaseModel):
    id: str
    dataset_id: str
    nombre: str
    descripcion: Optional[str] = None
    semilla_random: int
    particion_tipo: str
    estado: str
    progreso_pct: int
    logs_sanitizados: str
    inicio_ts: Optional[datetime] = None
    fin_ts: Optional[datetime] = None
    created_at: datetime
    modelos_count: Optional[int] = 0

    class Config:
        from_attributes = True

# --- Model & Metrics Schemas ---
class MetricaItem(BaseModel):
    tarea: str
    subgrupo: str
    split: str
    accuracy: float
    precision: float
    recall: float
    specificity: float
    f1_score: float
    roc_auc: float
    pr_auc: float
    brier_score: float
    ece_calibracion: float
    umbral_optimo: float
    ci_json: Optional[Dict[str, Any]] = None

class ModeloDetailResponse(BaseModel):
    id: str
    experimento_id: str
    codigo: str
    nombre: str
    familia: str
    tarea: str
    version: str
    estado_aprobacion: str
    model_card_json: Optional[Dict[str, Any]] = None
    hiperparametros_json: Optional[Dict[str, Any]] = None
    metricas_resumen_json: Optional[Dict[str, Any]] = None
    es_mejor_modelo: bool
    metricas: List[MetricaItem] = []
    created_at: datetime

    class Config:
        from_attributes = True

class ModelComparisonRow(BaseModel):
    codigo: str
    nombre: str
    familia: str
    tarea: str
    # Anemia metrics
    anemia_auc: float
    anemia_pr_auc: float
    anemia_f1: float
    anemia_sensitivity: float
    anemia_specificity: float
    anemia_brier: float
    anemia_ece: float
    # Stunting metrics
    stunting_auc: float
    stunting_pr_auc: float
    stunting_f1: float
    stunting_sensitivity: float
    stunting_specificity: float
    stunting_brier: float
    stunting_ece: float
    # Multi-task balance
    auc_promedio: float
    negative_transfer_detectado: bool
    estado_aprobacion: str

# --- Report Schemas ---
class ReporteResponse(BaseModel):
    id: str
    titulo: str
    tipo: str # PDF / EXCEL
    dataset_id: Optional[str] = None
    experimento_id: Optional[str] = None
    modelo_id: Optional[str] = None
    file_size_bytes: int
    es_sintetico: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Audit Schema ---
class AuditoriaItem(BaseModel):
    id: str
    usuario_email: Optional[str] = None
    accion: str
    entidad: str
    entidad_id: Optional[str] = None
    detalles: Optional[Dict[str, Any]] = None
    exito: bool
    timestamp: datetime

    class Config:
        from_attributes = True
