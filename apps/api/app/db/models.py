import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nombre = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False, default="investigador") # admin, investigador, analista, lector
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    usuario_id = Column(String(36), nullable=True)
    usuario_email = Column(String(255), nullable=True)
    accion = Column(String(100), nullable=False) # e.g. LOGIN, UPLOAD_DATASET, RUN_TRAINING, PREDICT, EXPORT_REPORT
    entidad = Column(String(100), nullable=False) # datasets, modelos, predicciones, etc.
    entidad_id = Column(String(100), nullable=True)
    detalles = Column(JSON, nullable=True)
    ip_origen = Column(String(100), nullable=True)
    exito = Column(Boolean, default=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now, index=True)

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    origen = Column(String(50), nullable=False) # ENDES, DHS, SINTETICO, JME_AGREGADO
    pais = Column(String(100), default="Perú")
    anio = Column(Integer, nullable=False)
    total_registros = Column(Integer, default=0)
    total_hogares = Column(Integer, default=0)
    es_sintetico = Column(Boolean, default=False, index=True)
    archivo_path = Column(String(500), nullable=True)
    checksum = Column(String(128), nullable=True)
    version_reglas = Column(String(100), default="OMS 2024 / INEI 2024")
    metadata_json = Column(JSON, nullable=True)
    calidad_resumen_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    hogares = relationship("HogarAnonimizado", back_populates="dataset", cascade="all, delete-orphan")
    ninos = relationship("NinoAnonimizado", back_populates="dataset", cascade="all, delete-orphan")
    experimentos = relationship("Experimento", back_populates="dataset")

class HogarAnonimizado(Base):
    __tablename__ = "hogares_anonimizados"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    hogar_pseudonimo = Column(String(100), nullable=False, index=True)
    conglomerado_psu = Column(String(50), nullable=False, index=True)
    estrato = Column(String(50), nullable=True)
    factor_expansion = Column(Float, default=1.0)
    quintil_riqueza = Column(Integer, default=3) # 1=Muy pobre, 5=Muy rico
    agua_potable = Column(Integer, default=1) # 1=Red publica/mejorada, 0=No tratada
    saneamiento = Column(Integer, default=1) # 1=Red/letrina mejorada, 0=Sin red
    material_piso = Column(String(50), default="cemento") # tierra, cemento, parquet/madera, otro
    electricidad = Column(Integer, default=1)
    combustible_cocina = Column(String(50), default="gas") # gas, leña/carbon, bosta, otro
    miembros_hogar = Column(Integer, default=4)
    area_residencia = Column(String(20), default="Urbana") # Urbana / Rural
    departamento = Column(String(100), default="Lima", index=True)
    ubigeo = Column(String(10), default="15")
    altitud_msnm = Column(Float, default=150.0)
    region_natural = Column(String(50), default="Costa") # Costa, Sierra, Selva
    created_at = Column(DateTime(timezone=True), default=utc_now)

    dataset = relationship("Dataset", back_populates="hogares")
    ninos = relationship("NinoAnonimizado", back_populates="hogar")

class NinoAnonimizado(Base):
    __tablename__ = "ninos_anonimizados"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    hogar_id = Column(String(36), ForeignKey("hogares_anonimizados.id", ondelete="CASCADE"), nullable=False, index=True)
    nino_pseudonimo = Column(String(100), nullable=False, index=True)
    sexo = Column(String(10), default="M") # M / F
    edad_meses = Column(Integer, nullable=False, index=True) # 0 to 59
    orden_nacimiento = Column(Integer, default=1)
    edad_madre = Column(Integer, default=26)
    educacion_madre = Column(String(50), default="Secundaria") # Sin nivel, Primaria, Secundaria, Superior
    controles_prenatales = Column(Integer, default=6)
    peso_nacimiento_g = Column(Float, default=3100.0)
    lactancia_materna = Column(Integer, default=1) # 1=Lactancia exclusiva/adecuada, 0=No
    suplemento_hierro = Column(Integer, default=0) # 1=Si recibio suplemento en ultimos 6 meses
    created_at = Column(DateTime(timezone=True), default=utc_now)

    dataset = relationship("Dataset", back_populates="ninos")
    hogar = relationship("HogarAnonimizado", back_populates="ninos")
    medicion = relationship("Medicion", back_populates="nino", uselist=False, cascade="all, delete-orphan")

class Medicion(Base):
    __tablename__ = "mediciones"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    nino_id = Column(String(36), ForeignKey("ninos_anonimizados.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Hemoglobina (Observada)
    hemoglobina_observada = Column(Float, nullable=True) # g/dL
    factor_ajuste_altitud = Column(Float, default=0.0) # g/dL
    hemoglobina_ajustada = Column(Float, nullable=True) # g/dL
    anemia_observada = Column(Integer, nullable=True) # 0=No, 1=Si, None=No evaluable
    anemia_severidad = Column(String(50), default="No evaluable") # Normal, Leve, Moderada, Severa, No evaluable
    anemia_evaluable = Column(Boolean, default=False) # True if edad_meses >= 6 and valid Hb

    # Antropometria (Observada)
    talla_cm = Column(Float, nullable=True)
    peso_kg = Column(Float, nullable=True)
    haz = Column(Float, nullable=True) # Z-score talla/edad OMS
    waz = Column(Float, nullable=True) # Z-score peso/edad OMS
    whz = Column(Float, nullable=True) # Z-score peso/talla OMS
    desnutricion_cronica_observada = Column(Integer, nullable=True) # 0=No, 1=Si (HAZ < -2)
    stunting_severidad = Column(String(50), default="Normal") # Normal, Moderada (-3 <= HAZ < -2), Severa (HAZ < -3)
    stunting_evaluable = Column(Boolean, default=False)

    # Clasificacion epidemiologica conjunta observada
    clasificacion_conjunta = Column(String(50), default="No evaluable") # Ninguno, Solo Anemia, Solo Desnutrición, Ambos, No evaluable
    version_reglas = Column(String(100), default="OMS 2024 / INEI")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    nino = relationship("NinoAnonimizado", back_populates="medicion")

class Experimento(Base):
    __tablename__ = "experimentos"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    semilla_random = Column(Integer, default=42)
    particion_tipo = Column(String(100), default="Estratificada por Conglomerados")
    train_pct = Column(Float, default=0.70)
    val_pct = Column(Float, default=0.15)
    test_pct = Column(Float, default=0.15)
    variables_predictoras_json = Column(JSON, nullable=True) # Lista de covariables autorizadas pre-medición
    estado = Column(String(50), default="creado") # creado, en_progreso, completado, fallido, cancelado
    progreso_pct = Column(Integer, default=0)
    logs_sanitizados = Column(Text, default="")
    inicio_ts = Column(DateTime(timezone=True), nullable=True)
    fin_ts = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    dataset = relationship("Dataset", back_populates="experimentos")
    modelos = relationship("Modelo", back_populates="experimento", cascade="all, delete-orphan")

class Modelo(Base):
    __tablename__ = "modelos"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experimento_id = Column(String(36), ForeignKey("experimentos.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo = Column(String(10), nullable=False) # M1, M2, M3, M4, M5
    nombre = Column(String(100), nullable=False) # Logistic Regression, Random Forest, CatBoost, Multi-Task NN, MTL + XGBoost
    familia = Column(String(100), nullable=False)
    tarea = Column(String(50), default="multisalida") # anemia, desnutricion, multisalida
    version = Column(String(20), default="1.0.0")
    artefacto_path = Column(String(500), nullable=True)
    estado_aprobacion = Column(String(50), default="experimental") # experimental, validado_internamente, aprobado_investigacion
    model_card_json = Column(JSON, nullable=True)
    hiperparametros_json = Column(JSON, nullable=True)
    metricas_resumen_json = Column(JSON, nullable=True)
    es_mejor_modelo = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    experimento = relationship("Experimento", back_populates="modelos")
    metricas = relationship("Metrica", back_populates="modelo", cascade="all, delete-orphan")
    predicciones = relationship("Prediccion", back_populates="modelo")

class Metrica(Base):
    __tablename__ = "metricas"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    modelo_id = Column(String(36), ForeignKey("modelos.id", ondelete="CASCADE"), nullable=False, index=True)
    tarea = Column(String(50), nullable=False) # anemia, desnutricion, conjunta
    subgrupo = Column(String(100), default="General") # General, Urbano, Rural, Femenino, Masculino, Selva, Sierra, Costa
    split = Column(String(20), default="test") # train, val, test
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True) # Sensibilidad
    specificity = Column(Float, nullable=True) # Especificidad
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    pr_auc = Column(Float, nullable=True)
    brier_score = Column(Float, nullable=True)
    ece_calibracion = Column(Float, nullable=True)
    umbral_optimo = Column(Float, default=0.5)
    ci_json = Column(JSON, nullable=True) # IC 95% bootstrap: {roc_auc: [lower, upper], ...}
    created_at = Column(DateTime(timezone=True), default=utc_now)

    modelo = relationship("Modelo", back_populates="metricas")

class Prediccion(Base):
    __tablename__ = "predicciones"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    modelo_id = Column(String(36), ForeignKey("modelos.id", ondelete="SET NULL"), nullable=True)
    nino_referencia_id = Column(String(100), nullable=True)
    input_covariables_json = Column(JSON, nullable=False) # Only pre-measurement features
    prob_anemia = Column(Float, nullable=False)
    prob_desnutricion = Column(Float, nullable=False)
    riesgo_anemia = Column(String(50), default="Bajo") # Bajo, Moderado, Alto
    riesgo_desnutricion = Column(String(50), default="Bajo")
    riesgo_conjunto = Column(String(100), default="Bajo riesgo simultáneo")
    es_sintetico = Column(Boolean, default=True)
    procedencia = Column(String(50), default="individual") # individual, lote
    advertencias_clinicas = Column(Text, default="Herramienta de investigación y apoyo a vigilancia. No sustituye evaluación clínica.")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    modelo = relationship("Modelo", back_populates="predicciones")
    explicacion = relationship("Explicacion", back_populates="prediccion", uselist=False, cascade="all, delete-orphan")

class Explicacion(Base):
    __tablename__ = "explicaciones"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    modelo_id = Column(String(36), nullable=False)
    prediccion_id = Column(String(36), ForeignKey("predicciones.id", ondelete="CASCADE"), nullable=False, unique=True)
    tarea = Column(String(50), default="multisalida")
    base_value_anemia = Column(Float, default=0.0)
    base_value_desnutricion = Column(Float, default=0.0)
    shap_anemia_json = Column(JSON, nullable=True) # {feature_name: shap_value, ...}
    shap_desnutricion_json = Column(JSON, nullable=True)
    top_factores_anemia = Column(JSON, nullable=True)
    top_factores_desnutricion = Column(JSON, nullable=True)
    disclaimer = Column(String(255), default="Asociaciones predictivas del modelo matemático, NO causalidad médica demostrada.")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    prediccion = relationship("Prediccion", back_populates="explicacion")

class Reporte(Base):
    __tablename__ = "reportes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    titulo = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=False) # PDF, EXCEL
    dataset_id = Column(String(36), nullable=True)
    experimento_id = Column(String(36), nullable=True)
    modelo_id = Column(String(36), nullable=True)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    es_sintetico = Column(Boolean, default=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

