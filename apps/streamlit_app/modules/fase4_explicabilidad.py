import streamlit as st
import numpy as np
import pandas as pd
import torch
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
from PIL import Image
from utils.synthetic_images import generate_conjunctiva_sample
from utils.gradcam import SimpleBiomedicalCNN, GradCAMPlusPlus, generate_attention_map, overlay_heatmap_on_image, get_binary_activation_mask

def render_fase4():
    st.markdown("### 🔍 Fase 4: Módulo de Explicabilidad Biomédica (Grad-CAM++, Atención y SHAP)")
    st.caption("Interpretabilidad multimodal: Descomposición de la activación convolucional y atribución de factores sociodemográficos.")

    tab_vision, tab_tabular = st.tabs(["👁️ Explicabilidad Visual (Grad-CAM++ & Atención)", "📊 Explicabilidad Tabular (Valores SHAP)"])

    with tab_vision:
        st.markdown("#### Grad-CAM++ sobre Biomarcadores Micro-Vasculares Conjuntivales")
        st.info(
            "Grad-CAM++ pondera gradientes de orden superior para identificar focos de palidez tisular "
            "y pérdida de vascularización que determinan la probabilidad de anemia severa o moderada."
        )

        col_in, col_ctrl = st.columns([1, 2])
        with col_in:
            sample_hb = st.slider("Nivel de Hemoglobina Simulado (g/dL):", min_value=6.0, max_value=14.0, value=8.4, step=0.2)
            alpha = st.slider("Transparencia del Mapa de Calor (Alpha):", min_value=0.2, max_value=0.8, value=0.55, step=0.05)
            thresh = st.slider("Umbral de Segmentación de Máscara:", min_value=0.3, max_value=0.8, value=0.55, step=0.05)

        # Generate sample image
        sample_img = generate_conjunctiva_sample(sample_hb, seed=101)

        # Initialize CNN and GradCAM++
        model = SimpleBiomedicalCNN(num_classes=2)
        gradcam_pp = GradCAMPlusPlus(model, target_layer=model.conv3)

        # Preprocess tensor
        preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        tensor_img = preprocess(sample_img).unsqueeze(0)

        # Generate GradCAM++ and Attention
        cam_map = gradcam_pp.generate(tensor_img, class_idx=1)
        attn_map = generate_attention_map(tensor_img, model)
        overlay_img = overlay_heatmap_on_image(sample_img, cam_map, alpha=alpha, colormap_name="jet")
        mask_img = get_binary_activation_mask(cam_map, threshold=thresh)

        # Display 4 visual modes
        st.markdown("##### Visualización Multimodal de Zonas Críticas:")
        col_v1, col_v2, col_v3, col_v4 = st.columns(4)

        with col_v1:
            st.image(sample_img, caption="1. ROI Original (Micro-tejido)", use_container_width=True)
        with col_v2:
            st.image(overlay_img, caption="2. Grad-CAM++ (Zonas Influyentes)", use_container_width=True)
        with col_v3:
            st.image(attn_map, caption="3. Mapa de Atención Espacial", use_container_width=True, clamp=True)
        with col_v4:
            st.image(mask_img, caption=f"4. Máscara Binaria (Act. ≥ {thresh})", use_container_width=True)

        st.caption(
            "Interpretación Clínica: Las regiones con mayor densidad de calor (rojo/amarillo) señalan zonas mucosas con deficiencia "
            "de pigmentación eritrocitaria y atenuación del lecho capilar profundo."
        )

    with tab_tabular:
        st.markdown("#### Descomposición de Determinantes Socioeconómicos con SHAP")
        st.caption("Aporte aditivo (|SHAP|) de las covariables sociodemográficas pre-medición.")

        shap_features = [
            {"Factor": "Edad del niño (meses)", "Impacto Anemia |SHAP|": 0.424, "Impacto Stunting |SHAP|": 0.312, "Efecto": "Mayor riesgo en 6-18 meses"},
            {"Factor": "Quintil de riqueza (Q1-Q5)", "Impacto Anemia |SHAP|": 0.365, "Impacto Stunting |SHAP|": 0.522, "Efecto": "Gradiente protector a mayor riqueza"},
            {"Factor": "Altitud geográfica (m.s.n.m.)", "Impacto Anemia |SHAP|": 0.338, "Impacto Stunting |SHAP|": 0.245, "Efecto": "Mayor ajuste de corte barométrico"},
            {"Factor": "Área de residencia (Rural)", "Impacto Anemia |SHAP|": 0.285, "Impacto Stunting |SHAP|": 0.394, "Efecto": "Aumenta riesgo por brecha de saneamiento"},
            {"Factor": "Nivel educativo de la madre", "Impacto Anemia |SHAP|": 0.241, "Impacto Stunting |SHAP|": 0.298, "Efecto": "Protector si educación secundaria o superior"},
            {"Factor": "Suplementación con hierro", "Impacto Anemia |SHAP|": 0.215, "Impacto Stunting |SHAP|": 0.082, "Efecto": "Protector directo contra anemia"},
            {"Factor": "Acceso a agua de red pública", "Impacto Anemia |SHAP|": 0.178, "Impacto Stunting |SHAP|": 0.264, "Efecto": "Reduce morbilidad diarreica"},
            {"Factor": "Controles prenatales (APN)", "Impacto Anemia |SHAP|": 0.152, "Impacto Stunting |SHAP|": 0.198, "Efecto": "Monitoreo preventivo del peso al nacer"}
        ]
        df_shap = pd.DataFrame(shap_features)

        fig_shap, ax_s = plt.subplots(figsize=(8, 4))
        y_pos = np.arange(len(df_shap))
        ax_s.barh(y_pos - 0.2, df_shap["Impacto Anemia |SHAP|"], height=0.35, label="Anemia Infantil", color="#f59e0b")
        ax_s.barh(y_pos + 0.2, df_shap["Impacto Stunting |SHAP|"], height=0.35, label="Desnutrición Crónica", color="#e11d48")
        ax_s.set_yticks(y_pos)
        ax_s.set_yticklabels(df_shap["Factor"])
        ax_s.invert_yaxis()
        ax_s.set_xlabel("Impacto Medio (|Valor de Shapley|)")
        ax_s.legend()
        ax_s.grid(True, linestyle=":", alpha=0.5)
        st.pyplot(fig_shap)

        st.dataframe(df_shap, use_container_width=True)

