import streamlit as st
import sys
import platform
import torch

def render_fase0():
    st.markdown("### 🛠️ Fase 0: Preparación, Entorno y Configuración de DeepSeek Harness")
    st.info(
        "Esta fase establece los cimientos operacionales, la estructura modular del proyecto, "
        "el aislamiento de dependencias y la configuración del arnés de inferencia e ingeniería analítica DeepSeek."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 1. Arquitectura y Estructura del Proyecto")
        st.code(
            """apps/streamlit_app/
├── app.py                     # Entry point y navegación multipágina
├── modules/
│   ├── fase0_harness.py       # Configuración y arnés de ejecución
│   ├── fase1_datos.py         # Módulo de datos: imágenes y metadata
│   ├── fase2_entrenamiento.py # Entrenamiento Nested CV 5x3 + Optuna
│   ├── fase3_evaluacion.py    # Evaluación, matrices y tests estadísticos
│   ├── fase4_explicabilidad.py# Grad-CAM++, mapas atención, SHAP
│   ├── fase5_reportes.py      # Exportación 600 DPI (PDF/Word/Excel)
│   ├── fase6_inferencia.py    # Inferencia individual y severidad
│   └── fase7_optuna_ui.py     # Optimización hiperparámetros Optuna UI
└── utils/
    ├── gradcam.py             # Algoritmo Grad-CAM++ en PyTorch
    ├── synthetic_images.py    # Imágenes sintéticas biomédicas (ROI)
    └── report_utils.py        # Generación Word/PDF/DPI editorial""",
            language="bash"
        )

    with col2:
        st.markdown("#### 2. Estado del Entorno de Ejecución")
        st.write(f"**Sistema Operativo:** `{platform.system()} {platform.release()}`")
        st.write(f"**Versión de Python:** `{sys.version.split()[0]}`")
        st.write(f"**PyTorch:** `{torch.__version__}` (CUDA disponible: `{torch.cuda.is_available()}`)")
        st.write("**Dispositivo de Cómputo Seleccionado:** `CPU / PyTorch Float32 Engine`")

        st.markdown("#### 3. Configuración del Arnés DeepSeek (Prompt Engineering Harness)")
        st.markdown(
            """
            El **DeepSeek Harness** actúa como supervisor cognitivo y evaluador metodológico:
            - **Temperatura:** `0.1` (Inferencia determinística reproducible)
            - **Top-p:** `0.95`
            - **Directiva de Cero Fuga:** Supervisión estricta de variables en $X_{pre}$
            - **Modo:** Bioestadística y Machine Learning Científico
            """
        )

    st.markdown("---")
    st.markdown("#### 📋 Verificación de Dependencias Esenciales")
    deps = {
        "Streamlit": "UI Interactiva y Dashboards Multimodales",
        "PyTorch & Torchvision": "Redes Neuronales Multitarea, CNNs y Grad-CAM++",
        "Optuna": "Optimización Bayesiana (Tree-structured Parzen Estimator)",
        "Scikit-Learn & CatBoost": "Clasificadores M1-M3 y Validación Cruzada",
        "SHAP": "Valores de Shapley para Interpretabilidad de Modelos Tabulares",
        "python-docx & openpyxl": "Generación de Informes Editoriales y Libros Tabulares",
        "Matplotlib & Seaborn": "Renderizado Gráfico a 600 DPI para Publicaciones Q1"
    }

    cols = st.columns(3)
    for i, (k, v) in enumerate(deps.items()):
        with cols[i % 3]:
            st.success(f"✅ **{k}**: {v}")

