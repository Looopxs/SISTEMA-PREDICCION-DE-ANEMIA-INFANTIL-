import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from utils.synthetic_images import get_demo_image_batch

def get_base_microdata(n: int = 200, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    departamentos = ["Puno", "Cusco", "Lima", "Loreto", "Huancavelica", "Piura", "Arequipa", "San Martín"]
    areas = ["Urbana", "Rural"]
    sexos = ["M", "F"]

    edades = np.random.randint(0, 60, size=n)
    sexo = np.random.choice(sexos, size=n)
    depto = np.random.choice(departamentos, size=n)
    area = np.random.choice(areas, size=n, p=[0.65, 0.35])
    quintil = np.random.choice([1, 2, 3, 4, 5], size=n, p=[0.25, 0.22, 0.20, 0.18, 0.15])
    altitud = [3827 if d == "Puno" else (3399 if d == "Cusco" else (3676 if d == "Huancavelica" else 150)) for d in depto]

    # Altitud adjustment factor
    alt_factor = [round(-0.0645 * (a/1000) + 0.0567 * ((a/1000)**2), 2) if a >= 1000 else 0.0 for a in altitud]

    # Hemoglobina observada y ajustada
    hb_obs = np.round(np.random.normal(10.8, 1.5, size=n) + (np.array(alt_factor) * 0.9), 1)
    hb_ajust = np.round(hb_obs - np.array(alt_factor), 1)

    # Anemia solo evaluable si edad >= 6
    anemia_eval = edades >= 6
    anemia_obs = np.where(anemia_eval, np.where(hb_ajust < 11.0, 1, 0), np.nan)

    # HAZ observada
    haz = np.round(np.random.normal(-1.3, 1.1, size=n) - (0.5 * (area == "Rural")), 2)
    stunting_obs = np.where(haz < -2.0, 1, 0)

    df = pd.DataFrame({
        "id_nino": [f"PER-2024-{i+1:04d}" for i in range(n)],
        "edad_meses": edades,
        "sexo": sexo,
        "departamento": depto,
        "area_residencia": area,
        "altitud_msnm": altitud,
        "quintil_riqueza": quintil,
        "educacion_madre": np.random.choice(["Primaria", "Secundaria", "Superior"], size=n),
        "acceso_agua_red": np.random.choice([1, 0], size=n, p=[0.75, 0.25]),
        "acceso_saneamiento": np.random.choice([1, 0], size=n, p=[0.68, 0.32]),
        "suplemento_hierro": np.random.choice([1, 0], size=n, p=[0.42, 0.58]),
        "conglomerado_psu": np.random.randint(100, 150, size=n),
        "factor_expansion": np.round(np.random.uniform(80.0, 320.0, size=n), 2),
        "hemoglobina_observada": hb_obs,
        "ajuste_altitud": alt_factor,
        "hemoglobina_ajustada": hb_ajust,
        "anemia_evaluable": anemia_eval,
        "anemia_observada": anemia_obs,
        "haz_talla_edad": haz,
        "stunting_observado": stunting_obs
    })
    return df

def render_fase1():
    st.markdown("### 📊 Fase 1: MVP — Módulo de Ingestión, Imágenes y Metadata")
    st.caption("Carga de imágenes no invasivas, editor interactivo de microdatos y validación de consistencia epidemiológica.")

    tab1, tab2, tab3 = st.tabs(["🖼️ Carga de Imágenes (Dataset Público)", "📝 Editor de Metadata", "📈 Estadística Descriptiva Explicable"])

    with tab1:
        st.markdown("#### Repositorio de Imágenes Biomédicas (Región Conjuntival/Palmar)")
        st.info(
            "Principio Ético Obligatorio (PROY2.docx): Para resguardar la identidad infantil, "
            "se emplean exclusivamente regiones de interés micro-vasculares (conjuntiva palpebral y lecho ungueal) "
            "sin rostros de niños ni datos biométricos sensibles."
        )

        n_samples = st.slider("Número de muestras a visualizar:", min_value=4, max_value=12, value=6, step=2)
        samples = get_demo_image_batch(n_samples=n_samples)

        cols = st.columns(3)
        for i, s in enumerate(samples):
            with cols[i % 3]:
                st.image(s["image"], caption=f"{s['id']} | Hb: {s['hemoglobina_g_dl']} g/dL ({s['estado_anemia']})", use_container_width=True)
                st.caption(f"Anatomía: {s['region_anatomica']}")

    with tab2:
        st.markdown("#### Editor Dinámico de Metadata y Microdatos")
        st.caption("Inspeccione y modifique valores directamente en la tabla editable. Las modificaciones se propagan al análisis.")

        if "df_microdata" not in st.session_state:
            st.session_state.df_microdata = get_base_microdata()

        edited_df = st.data_editor(
            st.session_state.df_microdata,
            num_rows="dynamic",
            use_container_width=True,
            height=320
        )
        st.session_state.df_microdata = edited_df

        st.markdown("##### 🔍 Validación de Grupos y Reglas de Consistencia:")
        col_v1, col_v2, col_v3 = st.columns(3)
        total = len(edited_df)
        valid_anemia = edited_df["anemia_evaluable"].sum()
        valid_stunting = edited_df["haz_talla_edad"].notna().sum()

        with col_v1:
            st.metric("Total Observaciones", total)
        with col_v2:
            st.metric("Elegibles para Anemia (≥ 6m)", f"{valid_anemia} ({valid_anemia/max(1, total)*100:.1f}%)")
        with col_v3:
            st.metric("Elegibles para Stunting (0–59m)", f"{valid_stunting} ({valid_stunting/max(1, total)*100:.1f}%)")

    with tab3:
        st.markdown("#### Estadística Descriptiva e Interpretabilidad Epidemiológica")
        df = st.session_state.df_microdata

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("##### Distribución de Hemoglobina Ajustada por Altitud (OMS 2024)")
            fig, ax = plt.subplots(figsize=(6, 4))
            eval_mask = df["anemia_evaluable"] == True
            sns.histplot(df.loc[eval_mask, "hemoglobina_ajustada"], kde=True, ax=ax, color="#f59e0b", bins=15)
            ax.axvline(11.0, color="red", linestyle="--", label="Punto de Corte Anemia (11.0 g/dL)")
            ax.set_xlabel("Hemoglobina Ajustada (g/dL)")
            ax.set_ylabel("Frecuencia")
            ax.legend()
            st.pyplot(fig)
            st.caption("Interpretabilidad: La distribución se desplaza a la izquierda en zonas de gran altitud al aplicar la corrección por hipoxia barométrica.")

        with col_g2:
            st.markdown("##### Gradiente de Retraso de Crecimiento (HAZ) por Quintil de Riqueza")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            sns.boxplot(x="quintil_riqueza", y="haz_talla_edad", data=df, hue="quintil_riqueza", palette="Blues_r", legend=False, ax=ax2)
            ax2.axhline(-2.0, color="red", linestyle="--", label="Límite Stunting (-2.0 DE)")
            ax2.set_xlabel("Quintil de Riqueza (1 = Más Pobre, 5 = Más Rico)")
            ax2.set_ylabel("Z-score Talla para la Edad (HAZ)")
            ax2.legend()
            st.pyplot(fig2)
            st.caption("Explicabilidad: Evidencia el gradiente socioeconómico donde el quintil 1 concentra los z-scores más deficitarios.")

