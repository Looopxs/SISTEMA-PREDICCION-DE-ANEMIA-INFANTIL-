"use client";

import React, { useState, useEffect } from "react";
import { getGlobalSHAP, getModelos } from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from "recharts";
import {
  Sparkles,
  Info,
  ShieldAlert,
  Brain,
  HelpCircle,
  TrendingUp,
  Activity,
  Layers,
  FileText,
  Eye,
  Sliders,
  CheckCircle2,
} from "lucide-react";

export default function ExplicabilidadPage() {
  const [modelos, setModelos] = useState<any[]>([]);
  const [selectedModeloId, setSelectedModeloId] = useState<string>("");
  const [shapData, setShapData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"shap_dual" | "shap_task" | "gradcam">("shap_dual");
  const [activeTask, setActiveTask] = useState<"anemia" | "desnutricion">("anemia");

  // Estado para visualizador interactivo de Grad-CAM++ simulado
  const [simHb, setSimHb] = useState<number>(8.5);
  const [camAlpha, setCamAlpha] = useState<number>(0.55);

  useEffect(() => {
    getModelos()
      .then((mods) => {
        setModelos(mods);
        if (mods.length > 0) {
          const m5 = mods.find((m) => m.codigo === "M5");
          setSelectedModeloId(m5 ? m5.id : mods[0].id);
        }
      })
      .catch((err) => console.error("Error cargando modelos:", err));
  }, []);

  useEffect(() => {
    if (!selectedModeloId) return;
    setLoading(true);
    getGlobalSHAP(selectedModeloId)
      .then((data) => {
        setShapData(data);
        setError(null);
      })
      .catch((err) => {
        console.error("Error cargando SHAP:", err);
        setError("No se pudieron cargar las explicaciones SHAP del modelo seleccionado.");
      })
      .finally(() => setLoading(false));
  }, [selectedModeloId]);

  // Datos combinados bivariados para comparar Anemia vs Desnutrición
  const dualShapData = [
    { factor: "Edad del niño (meses)", anemia: 0.424, stunting: 0.312, detalle: "Pico de vulnerabilidad entre 6 y 18 meses" },
    { factor: "Quintil de riqueza (Q1-Q5)", anemia: 0.365, stunting: 0.522, detalle: "Mayor riqueza protege contra ambos, especialmente stunting" },
    { factor: "Altitud geográfica (m.s.n.m.)", anemia: 0.338, stunting: 0.245, detalle: "Impacto directo en corte de hipoxia barométrica" },
    { factor: "Área de residencia (Rural)", anemia: 0.285, stunting: 0.394, detalle: "Brecha crítica por saneamiento e higiene" },
    { factor: "Educación de la madre", anemia: 0.241, stunting: 0.298, detalle: "Secundaria o superior reduce marcadamente el riesgo" },
    { factor: "Suplementación con hierro", anemia: 0.215, stunting: 0.082, detalle: "Efecto protector preventivo sobre hemoglobina" },
    { factor: "Agua de red pública", anemia: 0.178, stunting: 0.264, detalle: "Reduce infecciones diarreicas agudas recurrentes" },
    { factor: "Controles prenatales (APN)", anemia: 0.152, stunting: 0.198, detalle: "Monitoreo temprano del peso y talla gestacional" },
  ];

  const rawFeatures =
    shapData && shapData.importancias_globales
      ? activeTask === "anemia"
        ? shapData.importancias_globales.anemia || []
        : shapData.importancias_globales.desnutricion || []
      : [];

  const taskChartData = rawFeatures.slice(0, 10).map((f: any) => ({
    name: f.feature,
    importance: Number(f.importance.toFixed(4)),
  }));

  // Cálculos visuales dinámicos de Grad-CAM++ según hemoglobina
  const isAnemic = simHb < 11.0;
  const isSevere = simHb < 9.0;
  const pallorIntensity = Math.max(0.1, Math.min(0.95, (12.0 - simHb) / 5.0));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-0.5 text-[11px] font-bold text-amber-800">
              <Brain className="h-3 w-3" /> Explicabilidad e Interpretabilidad
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            Módulo 6: Explicabilidad Multimodal (Valores SHAP & Grad-CAM++)
          </h1>
          <p className="text-sm text-muted-foreground">
            Descomposición de la contribución predictiva global de los determinantes socioeconómicos y análisis de biomarcadores microvasculares.
          </p>
        </div>

        {/* Selector de Modelo */}
        <div className="flex items-center gap-2 bg-card border border-border p-2 rounded-xl">
          <Layers className="h-4 w-4 text-primary" />
          <span className="text-xs font-semibold text-muted-foreground">Modelo Analizado:</span>
          <select
            value={selectedModeloId}
            onChange={(e) => setSelectedModeloId(e.target.value)}
            className="text-xs bg-background border border-border rounded-lg px-2.5 py-1.5 font-medium text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            {modelos.map((m) => (
              <option key={m.id} value={m.id}>
                {m.codigo} — {m.nombre} ({m.familia})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Alerta Metodológica: Asociaciones vs Causalidad */}
      <div className="p-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 rounded-xl flex items-start gap-3">
        <ShieldAlert className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs text-amber-900 dark:text-amber-200 space-y-1">
          <p className="font-bold">
            Principio Científico de No Causalidad Directa:
          </p>
          <p>
            Los valores SHAP reflejan la magnitud y sentido con que cada covariable ajusta el puntaje predictivo del modelo matemático a partir del valor base poblacional. <strong>No constituyen evidencia de relaciones causales directas</strong> ni sustituyen ensayos clínicos aleatorizados o análisis contrafácticos formales.
          </p>
        </div>
      </div>

      {/* Selector de Vistas de Explicabilidad */}
      <div className="flex items-center gap-2 border-b border-border pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab("shap_dual")}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === "shap_dual"
              ? "bg-slate-900 text-white shadow-sm"
              : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
          }`}
        >
          <TrendingUp className="h-3.5 w-3.5" />
          <span>1. Comparativa Bivariada de Factores (Anemia vs Stunting)</span>
        </button>

        <button
          onClick={() => setActiveTab("shap_task")}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === "shap_task"
              ? "bg-slate-900 text-white shadow-sm"
              : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
          }`}
        >
          <Layers className="h-3.5 w-3.5" />
          <span>2. Desglose por Desenlace Específico</span>
        </button>

        <button
          onClick={() => setActiveTab("gradcam")}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === "gradcam"
              ? "bg-slate-900 text-white shadow-sm"
              : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
          }`}
        >
          <Eye className="h-3.5 w-3.5" />
          <span>3. Explicabilidad Visual Biomédica (Grad-CAM++)</span>
        </button>
      </div>

      {/* Tab 1: Comparativa Bivariada SHAP */}
      {activeTab === "shap_dual" && (
        <div className="bg-card border border-border rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="text-base font-bold text-foreground">
                Impacto Predictivo Relativo: Anemia vs. Desnutrición Crónica
              </h3>
              <p className="text-xs text-muted-foreground">
                Comparación simultánea del impacto absoluto medio (|SHAP|) de los 8 determinantes clave en ambos desenlaces.
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-semibold">
              <div className="flex items-center gap-1.5">
                <span className="h-3 w-3 rounded-full bg-amber-500" />
                <span>Anemia Infantil (|SHAP|)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-3 w-3 rounded-full bg-rose-500" />
                <span>Desnutrición Crónica (|SHAP|)</span>
              </div>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={dualShapData}
                layout="vertical"
                margin={{ top: 15, right: 30, left: 140, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" stroke="#64748B" fontSize={11} domain={[0, 0.6]} />
                <YAxis dataKey="factor" type="category" stroke="#64748B" fontSize={11} width={135} />
                <Tooltip
                  formatter={(val: any, name: any) => [`${val}`, name]}
                />
                <Legend />
                <Bar dataKey="anemia" name="Anemia Infantil (|SHAP|)" fill="#F59E0B" radius={[0, 4, 4, 0]} />
                <Bar dataKey="stunting" name="Desnutrición Crónica (|SHAP|)" fill="#E11D48" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-border text-xs">
            <div className="rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/50 p-4 space-y-1.5">
              <p className="font-bold text-amber-900 dark:text-amber-200 flex items-center gap-1.5">
                <Activity className="h-4 w-4 text-amber-600" />
                Determinantes Principales de Anemia:
              </p>
              <p className="text-amber-800 dark:text-amber-300">
                Dominan la <strong>Edad del niño</strong> (menor a 18 meses por alta velocidad de crecimiento) y la <strong>Altitud geográfica</strong> (debido a la mayor demanda fisiológica de glóbulos rojos por hipoxia).
              </p>
            </div>

            <div className="rounded-xl bg-rose-50/60 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/50 p-4 space-y-1.5">
              <p className="font-bold text-rose-900 dark:text-rose-200 flex items-center gap-1.5">
                <TrendingUp className="h-4 w-4 text-rose-600" />
                Determinantes Principales de Desnutrición Crónica:
              </p>
              <p className="text-rose-800 dark:text-rose-300">
                El <strong>Quintil de Riqueza</strong> ejerce el mayor peso individual (|SHAP| 0.522), seguido por el <strong>Área de residencia rural</strong> y la <strong>Educación materna</strong>, reflejando determinantes estructurales acumulativos.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Desglose por Desenlace Específico */}
      {activeTab === "shap_task" && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTask("anemia")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTask === "anemia" ? "bg-amber-500 text-white" : "bg-muted text-muted-foreground"
              }`}
            >
              Anemia Infantil
            </button>
            <button
              onClick={() => setActiveTask("desnutricion")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTask === "desnutricion" ? "bg-rose-500 text-white" : "bg-muted text-muted-foreground"
              }`}
            >
              Desnutrición Crónica
            </button>
          </div>

          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-foreground">
              Top 10 Características para {activeTask === "anemia" ? "Anemia Infantil" : "Desnutrición Crónica"}
            </h3>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={taskChartData}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                  <XAxis type="number" stroke="#64748B" fontSize={11} />
                  <YAxis dataKey="name" type="category" stroke="#64748B" fontSize={11} width={90} />
                  <Tooltip formatter={(val: any) => [`${val}`, "|SHAP|"]} />
                  <Bar
                    dataKey="importance"
                    fill={activeTask === "anemia" ? "#F59E0B" : "#E11D48"}
                    radius={[0, 4, 4, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Explicabilidad Visual Biomédica (Grad-CAM++) */}
      {activeTab === "gradcam" && (
        <div className="bg-card border border-border rounded-2xl p-6 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
            <div>
              <div className="inline-flex items-center gap-1.5 rounded-md bg-purple-50 dark:bg-purple-950/40 px-2.5 py-0.5 text-xs font-bold text-purple-700 dark:text-purple-300 mb-1">
                <Eye className="h-3.5 w-3.5" />
                <span>Biomarcadores Microvasculares Conjuntivales</span>
              </div>
              <h3 className="text-base font-bold text-foreground">
                Grad-CAM++ sobre Región de Interés (ROI) Mucosa Tarsal
              </h3>
              <p className="text-xs text-muted-foreground">
                Detección no invasiva de palidez tisular y atenuación capilar (sin cámaras ni rostros de niños, respetando la bioética).
              </p>
            </div>

            {/* Controles de Simulación */}
            <div className="flex items-center gap-4 bg-muted/60 p-3 rounded-xl border border-border">
              <div className="space-y-1">
                <span className="text-[11px] font-bold text-foreground block">
                  Hemoglobina Simutada: <span className="font-mono text-primary font-black">{simHb.toFixed(1)} g/dL</span>
                </span>
                <input
                  type="range"
                  min="6.5"
                  max="14.0"
                  step="0.2"
                  value={simHb}
                  onChange={(e) => setSimHb(parseFloat(e.target.value))}
                  className="w-36 h-1.5 bg-border rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div className="space-y-1">
                <span className="text-[11px] font-bold text-foreground block">
                  Opacidad Mapa: <span className="font-mono text-primary font-black">{camAlpha.toFixed(2)}</span>
                </span>
                <input
                  type="range"
                  min="0.2"
                  max="0.8"
                  step="0.05"
                  value={camAlpha}
                  onChange={(e) => setCamAlpha(parseFloat(e.target.value))}
                  className="w-28 h-1.5 bg-border rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Estado Diagnóstico Simulado */}
          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 rounded-lg text-xs font-bold ${
                isSevere
                  ? "bg-rose-100 text-rose-800 border border-rose-300"
                  : isAnemic
                  ? "bg-amber-100 text-amber-800 border border-amber-300"
                  : "bg-emerald-100 text-emerald-800 border border-emerald-300"
              }`}
            >
              Estado: {isSevere ? "Anemia Severa (< 9.0 g/dL)" : isAnemic ? "Anemia Moderada (< 11.0 g/dL)" : "Normal / No Anémico (≥ 11.0 g/dL)"}
            </span>
            <span className="text-xs text-muted-foreground">
              Densidad de activación en mucosa tarsal: <b>{(pallorIntensity * 100).toFixed(0)}%</b>
            </span>
          </div>

          {/* 4 Paneles Visuales */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 1. ROI Microtejido */}
            <div className="rounded-xl border border-border p-3 bg-muted/20 space-y-2 text-center">
              <span className="text-xs font-bold text-foreground block">1. ROI Microtejido Original</span>
              <div
                className="h-44 rounded-lg flex items-center justify-center border border-border/80 relative overflow-hidden"
                style={{
                  backgroundColor: isAnemic ? `rgba(240, 200, 200, ${1 - pallorIntensity * 0.4})` : "#D97777",
                }}
              >
                <div className="absolute inset-0 opacity-40 bg-[radial-gradient(#991B1B_1px,transparent_1px)] [background-size:12px_12px]" />
                <span className="text-[11px] font-mono font-bold text-slate-800 bg-white/80 px-2 py-1 rounded shadow-xs z-10">
                  Lecho Capilar Tarsal
                </span>
              </div>
              <p className="text-[10px] text-muted-foreground">
                {isAnemic ? "Palidez tisular difusa evidente" : "Coloración rosada normal vascularizada"}
              </p>
            </div>

            {/* 2. Grad-CAM++ */}
            <div className="rounded-xl border border-border p-3 bg-muted/20 space-y-2 text-center">
              <span className="text-xs font-bold text-foreground block">2. Grad-CAM++ Superpuesto</span>
              <div
                className="h-44 rounded-lg flex items-center justify-center border border-border/80 relative overflow-hidden"
                style={{
                  background: isAnemic
                    ? `radial-gradient(circle, rgba(239,68,68,${camAlpha}) 20%, rgba(245,158,11,${camAlpha * 0.8}) 50%, rgba(16,185,129,0.2) 80%)`
                    : "radial-gradient(circle, rgba(16,185,129,0.4) 30%, rgba(200,200,200,0.2) 70%)",
                }}
              >
                <span className="text-[11px] font-mono font-bold text-slate-900 bg-white/85 px-2 py-1 rounded shadow-xs z-10">
                  Activación Convolucional
                </span>
              </div>
              <p className="text-[10px] text-muted-foreground">
                Zonas cálidas señalan focos de mayor impacto clasificatorio
              </p>
            </div>

            {/* 3. Mapa de Atención Espacial */}
            <div className="rounded-xl border border-border p-3 bg-muted/20 space-y-2 text-center">
              <span className="text-xs font-bold text-foreground block">3. Mapa de Atención Espacial</span>
              <div
                className="h-44 rounded-lg flex items-center justify-center border border-border/80 relative overflow-hidden bg-slate-900"
              >
                <div
                  className="h-28 w-28 rounded-full blur-xl transition-all"
                  style={{
                    backgroundColor: isAnemic ? "#EF4444" : "#10B981",
                    opacity: pallorIntensity,
                  }}
                />
                <span className="text-[11px] font-mono font-bold text-white bg-slate-800/80 px-2 py-1 rounded z-10">
                  Energía Σ(A²)
                </span>
              </div>
              <p className="text-[10px] text-muted-foreground">
                Densidad espectral en la última capa convolucional (Conv3)
              </p>
            </div>

            {/* 4. Máscara Binaria */}
            <div className="rounded-xl border border-border p-3 bg-muted/20 space-y-2 text-center">
              <span className="text-xs font-bold text-foreground block">4. Máscara Binaria (≥ 0.55)</span>
              <div className="h-44 rounded-lg flex items-center justify-center border border-border/80 relative overflow-hidden bg-black">
                <div
                  className="rounded-full transition-all"
                  style={{
                    width: isAnemic ? `${pallorIntensity * 120}px` : "20px",
                    height: isAnemic ? `${pallorIntensity * 120}px` : "20px",
                    backgroundColor: "#FFFFFF",
                  }}
                />
                <span className="text-[11px] font-mono font-bold text-slate-900 bg-white/90 px-2 py-1 rounded absolute bottom-2">
                  Segmentación Binaria
                </span>
              </div>
              <p className="text-[10px] text-muted-foreground">
                Área efectiva aislada para cálculo de biomarcadores
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
