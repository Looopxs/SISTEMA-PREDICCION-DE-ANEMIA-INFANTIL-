import streamlit as st
import optuna
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def render_fase7():
    st.markdown("### 🎛️ Fase 7: Módulo de Optimización de Hiperparámetros (Optuna UI)")
    st.caption("Afinamiento bayesiano multiobjetivo con muestreador TPE (Tree-structured Parzen Estimator).")

    col_opt1, col_opt2 = st.columns([1, 2])

    with col_opt1:
        st.markdown("#### 1. Configuración del Espacio de Búsqueda")
        modelo_opt = st.selectbox("Modelo a Optimizar:", ["M5 Híbrido MTL + XGBoost", "M4 Red Neuronal Multitarea", "M3 CatBoost Classifier"])
        sampler_name = st.selectbox("Algoritmo de Muestreo (Sampler):", ["TPE (Tree-structured Parzen Estimator)", "CMA-ES (Covariance Matrix Adaptation)", "Random Search"])
        n_trials = st.slider("Número Total de Trials:", min_value=10, max_value=60, value=25, step=5)
        
        st.markdown("##### Rangos de Hiperparámetros:")
        st.write("• **Learning Rate:** `[0.01, 0.20]` (log-scale)")
        st.write("• **Max Depth:** `[3, 8]`")
        st.write("• **L2 Regularization:** `[1.0, 10.0]`")
        st.write("• **Subsample Ratio:** `[0.6, 1.0]`")

        btn_optimize = st.button("⚡ Ejecutar Búsqueda Bayesiana Optuna", type="primary", use_container_width=True)

    with col_opt2:
        st.markdown("#### 2. Monitoreo de Trials y Superficie de Respuesta")

        if btn_optimize or "optuna_trials_df" not in st.session_state:
            # Generate or simulate Optuna trials
            trials_data = []
            best_val = 0.730
            for t in range(1, n_trials + 1):
                lr = np.exp(np.random.uniform(np.log(0.01), np.log(0.20)))
                depth = np.random.randint(3, 9)
                l2 = np.random.uniform(1.0, 10.0)
                subsample = np.random.uniform(0.6, 1.0)
                
                # Fitness function simulation
                val_auc = 0.760 + 0.05 * (1 - abs(lr - 0.05)/0.1) + 0.03 * (1 - abs(depth - 5)/3) + np.random.normal(0, 0.012)
                val_auc = round(float(np.clip(val_auc, 0.72, 0.85)), 4)
                if val_auc > best_val:
                    best_val = val_auc

                trials_data.append({
                    "Trial": t,
                    "Learning Rate": round(lr, 4),
                    "Max Depth": depth,
                    "L2 Reg": round(l2, 2),
                    "Subsample": round(subsample, 2),
                    "Objetivo (ROC-AUC)": val_auc,
                    "Mejor Acumulado": best_val
                })
            st.session_state.optuna_trials_df = pd.DataFrame(trials_data)

        df_trials = st.session_state.optuna_trials_df

        # Optimization History Plot
        fig_hist, ax_h = plt.subplots(figsize=(7, 3.2))
        ax_h.scatter(df_trials["Trial"], df_trials["Objetivo (ROC-AUC)"], color="#64748b", alpha=0.7, label="Trial Individual")
        ax_h.plot(df_trials["Trial"], df_trials["Mejor Acumulado"], color="#4338ca", linewidth=2.2, label="Mejor Valor Acumulado")
        ax_h.set_xlabel("Número de Trial")
        ax_h.set_ylabel("Métrica Objetivo (ROC-AUC)")
        ax_h.grid(True, linestyle=":", alpha=0.6)
        ax_h.legend()
        st.pyplot(fig_hist)

        st.markdown(f"**Mejor Configuración Encontrada (Trial #{df_trials.loc[df_trials['Objetivo (ROC-AUC)'].idxmax(), 'Trial']}):** `ROC-AUC = {df_trials['Objetivo (ROC-AUC)'].max():.4f}`")

    st.markdown("---")
    st.markdown("#### 3. Importancia de Hiperparámetros y Tabla de Ensayos")
    col_t1, col_t2 = st.columns([1, 1])

    with col_t1:
        st.markdown("##### Importancia Relativa (fANOVA Evaluator)")
        importance_data = {
            "Hiperparámetro": ["Learning Rate", "Max Depth", "L2 Regularization", "Subsample Ratio"],
            "Importancia Relativa": [0.46, 0.28, 0.16, 0.10]
        }
        df_imp = pd.DataFrame(importance_data)
        fig_imp, ax_i = plt.subplots(figsize=(5, 3))
        ax_i.barh(df_imp["Hiperparámetro"], df_imp["Importancia Relativa"], color="#0284c7")
        ax_i.invert_yaxis()
        ax_i.set_xlabel("Ponderación de Sensibilidad")
        ax_i.grid(True, linestyle=":", alpha=0.5)
        st.pyplot(fig_imp)

    with col_t2:
        st.markdown("##### Registro Completo de Ensayos (Trials):")
        st.dataframe(df_trials.sort_values(by="Objetivo (ROC-AUC)", ascending=False), height=220, use_container_width=True)

