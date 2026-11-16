import streamlit as st
import sys
import os

# Add local path to sys.path so modules and utils can be imported cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from modules.fase0_harness import render_fase0
from modules.fase1_datos import render_fase1
from modules.fase2_entrenamiento import render_fase2
from modules.fase3_evaluacion import render_fase3
from modules.fase4_explicabilidad import render_fase4
from modules.fase5_reportes import render_fase5
from modules.fase6_inferencia import render_fase6
from modules.fase7_optuna_ui import render_fase7

# Page configuration
st.set_page_config(
    page_title="NutriPredict AI — Streamlit Research Suite",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Permanent Synthetic Data Banner (Non-negotiable scientific requirement)
st.warning(
    "⚠️ **DATOS SINTÉTICOS — NO REPRESENTAN LA REALIDAD** | "
    "Plataforma de Investigación y Vigilancia Nutricional Infantil (INV-02). "
    "Herramienta bioestadística y epidemiológica: NO emite diagnósticos médicos automáticos."
)

# Sidebar navigation
st.sidebar.title("🔬 NutriPredict AI")
st.sidebar.caption("Suite de Aprendizaje Multitarea y Explicabilidad (INV-02)")

fase_opciones = [
    "Fase 0: Preparación & DeepSeek Harness",
    "Fase 1: MVP — Módulo de Datos (Imágenes & Metadata)",
    "Fase 2: Módulo de Entrenamiento (Nested CV 5x3)",
    "Fase 3: Módulo de Evaluación Bioestadística",
    "Fase 4: Módulo de Explicabilidad (Grad-CAM++ & SHAP)",
    "Fase 5: Módulo de Reportes (600 DPI, Word, Excel)",
    "Fase 6: Módulo de Inferencia Pre-Medición",
    "Fase 7: Optimización Optuna UI"
]

seleccion = st.sidebar.radio("Navegación por Fases del Plan:", fase_opciones, index=1)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Alcance Científico Obligatorio:")
st.sidebar.markdown(
    """
    - **Ámbito:** Niños menores de 5 años (Perú).
    - **Desenlaces:**
      - Anemia Infantil (< 11.0 g/dL ajustado por altitud OMS 2024, 6–59m).
      - Desnutrición Crónica Infantil / Retraso del Crecimiento (HAZ < -2.0 DE, 0–59m).
    - **Cero Fuga de Datos:** $X_{pre}$ aislado de mediciones clínicas.
    """
)

# Routing
if seleccion == "Fase 0: Preparación & DeepSeek Harness":
    render_fase0()
elif seleccion == "Fase 1: MVP — Módulo de Datos (Imágenes & Metadata)":
    render_fase1()
elif seleccion == "Fase 2: Módulo de Entrenamiento (Nested CV 5x3)":
    render_fase2()
elif seleccion == "Fase 3: Módulo de Evaluación Bioestadística":
    render_fase3()
elif seleccion == "Fase 4: Módulo de Explicabilidad (Grad-CAM++ & SHAP)":
    render_fase4()
elif seleccion == "Fase 5: Módulo de Reportes (600 DPI, Word, Excel)":
    render_fase5()
elif seleccion == "Fase 6: Módulo de Inferencia Pre-Medición":
    render_fase6()
elif seleccion == "Fase 7: Optimización Optuna UI":
    render_fase7()

