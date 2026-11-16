import os
import io
import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def save_fig_600_dpi(fig: plt.Figure) -> bytes:
    """
    Exporta un objeto matplotlib Figure a un buffer de bytes con resolución editorial de 600 DPI.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=600, bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()

def generate_word_scientific_report(
    titulo: str,
    metricas_df: pd.DataFrame,
    mcnemar_dict: dict,
    bootstrap_ci_dict: dict,
    fig_roc_bytes: bytes = None,
    fig_shap_bytes: bytes = None
) -> bytes:
    """
    Genera un documento Word (.docx) formal para comité de investigación y publicación científica.
    """
    doc = Document()

    # Title styling
    title_p = doc.add_paragraph()
    title_run = title_p.add_run(titulo)
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 23, 42)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("Informe de Evaluación Experimental, Explicabilidad y Validación Bioestadística")
    sub_run.font.size = Pt(11)
    sub_run.font.italic = True
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("Fecha de generación: 2026-11-09 | Plataforma: NutriPredict AI (Streamlit Enterprise)")
    doc.add_paragraph("Ámbito: Niños menores de 5 años (Perú / América Latina) | Criterios OMS 2006 / 2024\n")

    # 1. Marco Metodológico y Cero Fuga
    h1 = doc.add_heading("1. Marco Metodológico y Garantía de No Fuga de Datos", level=1)
    p_meta = doc.add_paragraph(
        "Se implementó un protocolo de validación cruzada anidada (Nested Cross-Validation: 5 outer folds x 3 inner folds) "
        "combinado con optimización bayesiana de hiperparámetros (Optuna). Para garantizar imparcialidad científica absoluta, "
        "las covariables de entrada excluyen cualquier medición física (hemoglobina, talla, peso, z-scores HAZ/WAZ/WHZ), "
        "evaluando exclusivamente el perfil predictivo previo al tamizaje clínico directo."
    )

    # 2. Tabla Comparativa de Rendimiento
    doc.add_heading("2. Desempeño Comparativo de Modelos (Test Set Independiente)", level=1)
    
    # Add Table
    table = doc.add_table(rows=1, cols=len(metricas_df.columns))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    
    # Headers
    hdr_cells = table.rows[0].cells
    for i, col_name in enumerate(metricas_df.columns):
        hdr_cells[i].text = str(col_name)
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True

    # Data Rows
    for _, row in metricas_df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = f"{val:.4f}" if isinstance(val, (float, int)) and not isinstance(val, bool) and abs(val) < 100 else str(val)

    doc.add_paragraph("\nNota: AUC promedio refleja el balance multitarea entre la detección de anemia y desnutrición crónica.")

    # 3. Contraste de Hipótesis (McNemar y Bootstrap)
    doc.add_heading("3. Laboratorio Bioestadístico y Pruebas Pareadas", level=1)
    p_stat = doc.add_paragraph()
    p_stat.add_run(f"• Prueba Pareada de McNemar (M5 Híbrido vs M3 CatBoost):\n").bold = True
    p_stat.add_run(f"  - Chi-cuadrado (χ²): {mcnemar_dict.get('chi2', 0.0):.4f}\n")
    p_stat.add_run(f"  - Valor p: {mcnemar_dict.get('p_value', 1.0):.5f}\n")
    p_stat.add_run(f"  - Conclusión: {mcnemar_dict.get('interpretacion', 'Diferencia evaluada')}\n")

    p_ci = doc.add_paragraph()
    p_ci.add_run("• Intervalos de Confianza Bootstrap al 95% (1,000 réplicas):\n").bold = True
    for met, (low, high) in bootstrap_ci_dict.items():
        p_ci.add_run(f"  - {met}: IC 95% [{low:.4f}, {high:.4f}]\n")

    # 4. Figuras en Alta Resolución
    if fig_roc_bytes:
        doc.add_heading("4. Curvas Características de Rendimiento (600 DPI)", level=1)
        doc.add_picture(io.BytesIO(fig_roc_bytes), width=Inches(6.0))
        p_caption = doc.add_paragraph("Figura 1: Curvas ROC y Precision-Recall comparativas generadas a 600 DPI para publicación.")
        p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_caption.runs[0].font.italic = True

    if fig_shap_bytes:
        doc.add_heading("5. Explicabilidad Global y Local (Valores SHAP y Grad-CAM++)", level=1)
        doc.add_picture(io.BytesIO(fig_shap_bytes), width=Inches(6.0))
        p_cap2 = doc.add_paragraph("Figura 2: Descomposición de factores de Shapley (|SHAP|) y mapas de calor Grad-CAM++.")
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.runs[0].font.italic = True

    # 6. Declaración de Ética
    doc.add_heading("6. Declaración Ética y Limitaciones de Uso", level=1)
    doc.add_paragraph(
        "NutriPredict AI es una herramienta de apoyo a la investigación bioestadística y priorización comunitaria. "
        "NO constituye un dispositivo de diagnóstico médico automático ni reemplaza la toma de muestras de hemoglobina o mediciones antropométricas directas. "
        "Los datos demostrativos han sido procesados conforme a la Ley N° 29733 de Protección de Datos Personales del Perú."
    )

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

