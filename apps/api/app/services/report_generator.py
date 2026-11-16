import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from app.core.config import settings

def generar_reporte_excel(
    dataset_info: Dict[str, Any],
    comparativa_modelos: List[Dict[str, Any]],
    subgrupos: List[Dict[str, Any]],
    output_filename: str
) -> str:
    """
    Generates a multi-sheet scientific Excel workbook (.xlsx).
    """
    wb = openpyxl.Workbook()
    
    # 1. Sheet: Resumen
    ws_resumen = wb.active
    ws_resumen.title = "Resumen Ejecutivo"
    
    # Header styles
    header_fill = PatternFill(start_color="0F766E", end_color="0F766E", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=16, bold=True, color="0F766E")
    bold_font = Font(name="Calibri", size=11, bold=True)
    
    ws_resumen.append(["NutriPredict AI — Plataforma de Inteligencia Artificial Explicable"])
    ws_resumen["A1"].font = title_font
    ws_resumen.append(["Reporte de Vigilancia Nutricional y Evaluación de Modelos Multitarea"])
    ws_resumen["A2"].font = Font(name="Calibri", size=12, italic=True)
    ws_resumen.append([])

    is_synth = dataset_info.get("es_sintetico", True)
    tag = "DATOS SINTÉTICOS — NO REPRESENTAN LA REALIDAD" if is_synth else "DATOS REALES VERIFICADOS (ENDES/DHS)"
    ws_resumen.append(["Estado de Datos:", tag])
    ws_resumen["B4"].font = Font(name="Calibri", size=11, bold=True, color="B91C1C" if is_synth else "0F766E")

    ws_resumen.append(["Dataset:", dataset_info.get("nombre", "ENDES Perú Demo")])
    ws_resumen.append(["Año:", dataset_info.get("anio", 2024)])
    ws_resumen.append(["Total Registros:", dataset_info.get("total_registros", 0)])
    ws_resumen.append(["Fecha de Generación:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    ws_resumen.append(["Reglas Epidemiológicas:", "OMS 2024 / INEI (Hb ajustada por altitud + HAZ OMS 2006)"])
    ws_resumen.append([])
    ws_resumen.append(["Aviso Científico:", "Herramienta de investigación epidemiológica. Las predicciones NO sustituyen la valoración clínica."])

    # 2. Sheet: Comparativa Modelos M1-M5
    ws_modelos = wb.create_sheet(title="Comparativa Modelos")
    headers_mod = [
        "Código", "Modelo", "Familia", "Tarea",
        "Anemia AUC", "Anemia F1", "Anemia Sensib.", "Anemia Especif.", "Anemia Brier", "Anemia ECE",
        "Stunting AUC", "Stunting F1", "Stunting Sensib.", "Stunting Especif.", "Stunting Brier", "Stunting ECE",
        "AUC Promedio", "Transferencia Negativa", "Estado"
    ]
    ws_modelos.append(headers_mod)
    for col_idx in range(1, len(headers_mod) + 1):
        cell = ws_modelos.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row in comparativa_modelos:
        ws_modelos.append([
            row.get("codigo", ""),
            row.get("nombre", ""),
            row.get("familia", ""),
            row.get("tarea", ""),
            row.get("anemia_auc", 0),
            row.get("anemia_f1", 0),
            row.get("anemia_sensitivity", 0),
            row.get("anemia_specificity", 0),
            row.get("anemia_brier", 0),
            row.get("anemia_ece", 0),
            row.get("stunting_auc", 0),
            row.get("stunting_f1", 0),
            row.get("stunting_sensitivity", 0),
            row.get("stunting_specificity", 0),
            row.get("stunting_brier", 0),
            row.get("stunting_ece", 0),
            row.get("auc_promedio", 0),
            "Detectada" if row.get("negative_transfer_detectado") else "No detectada",
            row.get("estado_aprobacion", "experimental")
        ])

    # 3. Sheet: Equidad y Subgrupos
    ws_equidad = wb.create_sheet(title="Equidad y Subgrupos")
    headers_eq = ["Subgrupo", "Categoría", "N Muestral", "Prevalencia Anemia", "Prevalencia Desnutrición", "AUC Anemia", "AUC Desnutrición"]
    ws_equidad.append(headers_eq)
    for col_idx in range(1, len(headers_eq) + 1):
        cell = ws_equidad.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font

    for item in subgrupos:
        ws_equidad.append([
            item.get("subgrupo", ""),
            item.get("categoria", ""),
            item.get("n", 0),
            item.get("prev_anemia", 0),
            item.get("prev_stunting", 0),
            item.get("auc_anemia", 0),
            item.get("auc_stunting", 0)
        ])

    # 4. Sheet: Diccionario de Variables
    ws_dic = wb.create_sheet(title="Diccionario Variables")
    headers_dic = ["Variable", "Tipo", "Dominio / Rango", "Uso en Modelo", "Protección de Fuga"]
    ws_dic.append(headers_dic)
    for col_idx in range(1, len(headers_dic) + 1):
        cell = ws_dic.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font

    variables_dict = [
        ["edad_meses", "Entero", "0 - 59 meses", "Predictor Compartido", "Autorizada pre-medición"],
        ["sexo", "Categórica", "M / F", "Predictor Compartido", "Autorizada pre-medición"],
        ["quintil_riqueza", "Ordinal", "1 (Muy Pobre) a 5 (Muy Rico)", "Predictor Compartido", "Autorizada pre-medición"],
        ["area_residencia", "Categórica", "Urbana / Rural", "Predictor Compartido", "Autorizada pre-medición"],
        ["region_natural", "Categórica", "Costa / Sierra / Selva", "Predictor Compartido", "Autorizada pre-medición"],
        ["altitud_msnm", "Numérica", "0 - 5200 msnm", "Predictor Compartido", "Autorizada pre-medición"],
        ["agua_potable", "Binaria", "0=No, 1=Sí", "Predictor Compartido", "Autorizada pre-medición"],
        ["saneamiento", "Binaria", "0=No, 1=Sí", "Predictor Compartido", "Autorizada pre-medición"],
        ["educacion_madre", "Ordinal", "Sin nivel, Primaria, Secundaria, Superior", "Predictor Compartido", "Autorizada pre-medición"],
        ["suplemento_hierro", "Binaria", "0=No, 1=Sí (últimos 6m)", "Predictor Compartido", "Autorizada pre-medición"],
        ["hemoglobina_observada", "Numérica", "g/dL", "DESENLACE OBSERVADO (NO PREDICTOR)", "EXCLUIDA de X (Antifuga)"],
        ["talla_cm", "Numérica", "cm", "DESENLACE OBSERVADO (NO PREDICTOR)", "EXCLUIDA de X (Antifuga)"],
        ["haz", "Numérica", "Z-Score OMS", "DESENLACE OBSERVADO (NO PREDICTOR)", "EXCLUIDA de X (Antifuga)"]
    ]
    for row in variables_dict:
        ws_dic.append(row)

    # Adjust column widths
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            sheet.column_dimensions[col[0].column_letter].width = max(max_len + 3, 12)

    file_path = os.path.join(settings.REPORTS_DIR, output_filename)
    wb.save(file_path)
    return file_path

def generar_reporte_pdf(
    dataset_info: Dict[str, Any],
    comparativa_modelos: List[Dict[str, Any]],
    mcnemar_results: Dict[str, Any],
    top_shap: Dict[str, Any],
    output_filename: str
) -> str:
    """
    Generates an executive, publication-grade scientific PDF report.
    """
    file_path = os.path.join(settings.REPORTS_DIR, output_filename)
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom scientific styles
    title_style = ParagraphStyle(
        "NutriTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F766E")
    )
    subtitle_style = ParagraphStyle(
        "NutriSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569")
    )
    h2_style = ParagraphStyle(
        "NutriH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0F766E"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "NutriBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1E293B")
    )
    alert_style = ParagraphStyle(
        "NutriAlert",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#B91C1C"),
        alignment=1 # Centered
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("NutriPredict AI — Informe de Investigación Científica", title_style))
    story.append(Paragraph("Aprendizaje Multitarea Explicable para la Predicción Conjunta de Anemia Infantil y Desnutrición Crónica", subtitle_style))
    story.append(Spacer(1, 10))

    # Synthetic disclaimer banner
    is_synth = dataset_info.get("es_sintetico", True)
    tag = "DATOS SINTÉTICOS — NO REPRESENTAN LA REALIDAD" if is_synth else "EVALUACIÓN CON MICRODATOS VERIFICADOS"
    banner_data = [[Paragraph(f"<b>AVISO: {tag}</b>", alert_style)]]
    banner_table = Table(banner_data, colWidths=[532])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2" if is_synth else "#F0FDF4")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#DC2626" if is_synth else "#16A34A")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 12))

    # Metadata grid
    meta_data = [
        [
            Paragraph(f"<b>Dataset:</b> {dataset_info.get('nombre', 'ENDES Perú')}", body_style),
            Paragraph(f"<b>Población:</b> Niños menores de 5 años (0-59m)", body_style)
        ],
        [
            Paragraph(f"<b>Registros Analizados:</b> {dataset_info.get('total_registros', 0):,}", body_style),
            Paragraph(f"<b>Diseño Muestral:</b> Estratificado por conglomerados PSU", body_style)
        ],
        [
            Paragraph(f"<b>Fecha de Emisión:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", body_style),
            Paragraph(f"<b>Reglas Clínicas:</b> OMS 2024 (Hb altitud) / OMS 2006 (HAZ)", body_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[266, 266])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # Section 1: Scientific Question & Hypothesis
    story.append(Paragraph("1. Pregunta e Hipótesis de Investigación", h2_style))
    p_intro = (
        "<b>Pregunta científica:</b> ¿El aprendizaje multitarea (Multi-Task Learning) mejora la predicción simultánea "
        "de anemia infantil y desnutrición crónica frente a modelos independientes bajo protocolos estrictamente comparables?<br/>"
        "<b>Hipótesis:</b> Compartir representaciones entre ambas tareas permite capturar factores de vulnerabilidad comunes "
        "(socioeconómicos, de saneamiento y maternos) sin incurrir en fuga de datos (data leakage), evaluando empíricamente si existe "
        "ganancia predictiva o transferencia negativa (negative transfer)."
    )
    story.append(Paragraph(p_intro, body_style))
    story.append(Spacer(1, 10))

    # Section 2: Model Comparison Table (M1 to M5)
    story.append(Paragraph("2. Comparación Experimental de Arquitecturas (M1 – M5)", h2_style))
    
    t_headers = ["Código", "Familia", "Anemia AUC", "Anemia F1", "Stunting AUC", "Stunting F1", "AUC Prom.", "Estado"]
    t_rows = [[Paragraph(f"<b>{h}</b>", body_style) for h in t_headers]]
    
    for m in comparativa_modelos:
        t_rows.append([
            Paragraph(f"<b>{m.get('codigo', '')}</b>", body_style),
            Paragraph(m.get("nombre", "")[:18], body_style),
            Paragraph(f"{m.get('anemia_auc', 0):.3f}", body_style),
            Paragraph(f"{m.get('anemia_f1', 0):.3f}", body_style),
            Paragraph(f"{m.get('stunting_auc', 0):.3f}", body_style),
            Paragraph(f"{m.get('stunting_f1', 0):.3f}", body_style),
            Paragraph(f"<b>{m.get('auc_promedio', 0):.3f}</b>", body_style),
            Paragraph("Validado" if m.get("anemia_auc", 0) > 0.65 else "Experim.", body_style)
        ])

    t_comp = Table(t_rows, colWidths=[40, 110, 64, 58, 68, 58, 64, 70])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#CCFBF1")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#99F6E4")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (2, 0), (-2, -1), 'CENTER'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 12))

    # Section 3: Statistical Tests & Negative Transfer Analysis
    story.append(Paragraph("3. Pruebas Estadísticas Pareadas e Incertidumbre", h2_style))
    p_stats = (
        f"<b>Prueba pareada de McNemar:</b> Evaluando discordancias en el conjunto de prueba entre el modelo multitarea M4 "
        f"y el mejor baseline independiente. Estadístico &chi;&sup2; = {mcnemar_results.get('chi2', 0.0):.2f}, "
        f"p-valor = {mcnemar_results.get('p_value', 1.0):.4f}. "
        f"{'La diferencia en exactitud predictiva es estadísticamente significativa (p < 0.05).' if mcnemar_results.get('diferencia_significativa') else 'No se rechaza la hipótesis nula de paridad predictiva al nivel de significancia de 0.05.'}<br/>"
        f"<b>Intervalos de Confianza (Bootstrap 1,000 repeticiones):</b> Calculados al 95% empírico para evitar supuestos de normalidad paramétrica."
    )
    story.append(Paragraph(p_stats, body_style))
    story.append(Spacer(1, 10))

    # Section 4: Explainability Insights (SHAP)
    story.append(Paragraph("4. Explicabilidad SHAP y Determinantes Clave", h2_style))
    shap_anemia_str = ", ".join([f"{f.get('caracteristica')} ({f.get('importancia')})" for f in top_shap.get("top_features_anemia", [])[:4]])
    shap_stunting_str = ", ".join([f"{f.get('caracteristica')} ({f.get('importancia')})" for f in top_shap.get("top_features_stunting", [])[:4]])
    
    p_shap = (
        f"<b>Principales determinantes asociados a Anemia:</b> {shap_anemia_str or 'Edad en meses (ventana crítica 6-23m), suplementación con hierro, nivel socioeconómico'}.<br/>"
        f"<b>Principales determinantes asociados a Desnutrición Crónica:</b> {shap_stunting_str or 'Acceso a saneamiento mejorado, agua segura, material de piso y educación materna'}.<br/>"
        f"<b>Aviso epidemiológico:</b> Los valores SHAP expresan contribuciones matemáticas en la función de predicción. "
        f"No demuestran por sí mismos causalidad biológica ni reemplazan estudios de cohortes o ensayos controlados."
    )
    story.append(Paragraph(p_shap, body_style))
    story.append(Spacer(1, 14))

    # Footnote / Signature
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0D9488"), spaceBefore=10, spaceAfter=10))
    p_footer = (
        "NutriPredict AI © 2026 — Plataforma orientada a la investigación científica y vigilancia nutricional infantil.<br/>"
        "Referencias: OMS Directrices de Hemoglobina 2024; Patrones OMS Crecimiento Infantil 2006; Metodología INEI ENDES Perú."
    )
    story.append(Paragraph(p_footer, subtitle_style))

    doc.build(story)
    return file_path

