"use client";

import React, { useState, useEffect } from "react";
import { getReportes, generarReporte, getDownloadReporteUrl } from "@/lib/api";
import {
  FileText,
  Download,
  FileSpreadsheet,
  PlusCircle,
  Activity,
  CheckCircle2,
  Calendar,
  HardDrive,
  ShieldAlert,
  Sparkles,
} from "lucide-react";

export default function ReportesPage() {
  const [reportes, setReportes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState<"PDF" | "EXCEL" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadReportes = async () => {
    try {
      const data = await getReportes();
      setReportes(data);
    } catch (err: any) {
      console.error("Error al cargar reportes:", err);
      setError("No se pudieron cargar los reportes existentes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReportes();
  }, []);

  const handleGenerate = async (tipo: "PDF" | "EXCEL") => {
    setGenerating(tipo);
    setError(null);
    setSuccessMsg(null);
    try {
      const nuevo = await generarReporte(tipo);
      setSuccessMsg(
        `Reporte ${tipo} generado exitosamente: "${nuevo.titulo}". Listo para descargar.`
      );
      await loadReportes();
    } catch (err: any) {
      setError(err.message || `Error al generar reporte ${tipo}`);
    } finally {
      setGenerating(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            Módulo 9: Informes Científicos y Exportación de Datos
          </h1>
          <p className="text-sm text-muted-foreground">
            Generación de reportes de grado editorial en PDF y libros de cálculo tabulares en Excel (.xlsx) para auditoría, investigación y comités de ética.
          </p>
        </div>

        {/* Acciones Rápidas de Generación */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleGenerate("PDF")}
            disabled={generating !== null}
            className="px-4 py-2 bg-rose-600 hover:bg-rose-750 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors disabled:opacity-50 shadow-sm"
          >
            {generating === "PDF" ? (
              <Activity className="h-4 w-4 animate-spin" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
            Generar Informe Científico (PDF)
          </button>
          <button
            onClick={() => handleGenerate("EXCEL")}
            disabled={generating !== null}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors disabled:opacity-50 shadow-sm"
          >
            {generating === "EXCEL" ? (
              <Activity className="h-4 w-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="h-4 w-4" />
            )}
            Generar Libro Tabular (Excel)
          </button>
        </div>
      </div>

      {/* Notificaciones */}
      {successMsg && (
        <div className="p-4 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900 rounded-xl flex items-center gap-3 text-xs text-emerald-800 dark:text-emerald-200">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-xl flex items-center gap-3 text-xs text-destructive">
          <ShieldAlert className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Ficha Resumen de Contenido de los Reportes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 bg-card border border-border rounded-xl shadow-sm space-y-2">
          <div className="flex items-center gap-2 text-rose-600 font-semibold text-xs uppercase tracking-wider">
            <FileText className="h-4 w-4" />
            Estructura del Informe Científico PDF
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Documento formal maquetado con ReportLab que incluye: (1) Resumen ejecutivo y marco metodológico CRISP-DM; (2) Tabla comparativa head-to-head de modelos M1–M5; (3) Desglose de determinantes explicativos SHAP; (4) Diagnóstico de equidad y brechas territoriales; (5) Declaración de no-fuga y descargos bioéticos.
          </p>
        </div>

        <div className="p-4 bg-card border border-border rounded-xl shadow-sm space-y-2">
          <div className="flex items-center gap-2 text-emerald-600 font-semibold text-xs uppercase tracking-wider">
            <FileSpreadsheet className="h-4 w-4" />
            Estructura del Libro Excel (.xlsx)
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Libro de trabajo estructurado en pestañas especializadas con openpyxl: (1) `Resumen_Ejecutivo` (KPIs globales); (2) `Metricas_Modelos` (ROC-AUC, F1, Brier, ECE); (3) `Geografia_Departamental` (25 departamentos de Perú); (4) `Muestra_Microdatos` (registros anonimizados para reproducibilidad).
          </p>
        </div>
      </div>

      {/* Lista de Reportes Generados */}
      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <HardDrive className="h-4 w-4 text-primary" />
            Repositorio de Documentos Generados
          </h2>
          <span className="text-xs text-muted-foreground font-mono">
            {reportes.length} archivos
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-muted-foreground flex items-center justify-center gap-2">
            <Activity className="h-4 w-4 animate-spin text-primary" />
            Cargando lista de reportes...
          </div>
        ) : reportes.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <div className="mx-auto w-12 h-12 rounded-full bg-secondary flex items-center justify-center text-muted-foreground">
              <FileText className="h-6 w-6" />
            </div>
            <p className="text-xs text-muted-foreground">
              Aún no se han generado reportes. Utilice los botones superiores para compilar un PDF o Excel.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {reportes.map((rep) => {
              const isPdf = rep.tipo === "PDF";
              const downloadUrl = getDownloadReporteUrl(rep.id);
              return (
                <div
                  key={rep.id}
                  className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-muted/20 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`p-2.5 rounded-lg ${
                        isPdf
                          ? "bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400"
                          : "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400"
                      }`}
                    >
                      {isPdf ? <FileText className="h-5 w-5" /> : <FileSpreadsheet className="h-5 w-5" />}
                    </div>
                    <div>
                      <h3 className="text-xs font-bold text-foreground">{rep.titulo}</h3>
                      <div className="flex items-center gap-3 text-[11px] text-muted-foreground mt-1">
                        <span className="flex items-center gap-1 font-mono">
                          <Calendar className="h-3 w-3" />
                          {new Date(rep.creado_en).toLocaleString("es-PE")}
                        </span>
                        <span className="font-mono">
                          {(rep.file_size_bytes || rep.tamano_bytes) ? `${(((rep.file_size_bytes || rep.tamano_bytes)) / 1024).toFixed(1)} KB` : "—"}
                        </span>
                        <span className="px-1.5 py-0.2 rounded bg-secondary text-secondary-foreground text-[10px] font-mono">
                          {rep.tipo}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center">
                    <a
                      href={downloadUrl}
                      download
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3.5 py-1.5 bg-primary text-primary-foreground font-semibold text-xs rounded-md hover:bg-primary/90 transition-colors flex items-center gap-1.5 shadow-sm"
                    >
                      <Download className="h-3.5 w-3.5" />
                      Descargar Archivo
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

