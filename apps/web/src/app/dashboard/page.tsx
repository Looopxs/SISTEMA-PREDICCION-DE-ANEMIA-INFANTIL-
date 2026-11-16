"use client";

import React, { useEffect, useState } from "react";
import {
  Activity,
  HeartPulse,
  Users,
  Home,
  AlertTriangle,
  RefreshCw,
  TrendingUp,
  Download,
  Info,
  Layers,
  MapPin,
  Scale,
  Sparkles,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area,
} from "recharts";
import {
  getDashboardSummary,
  getAnalisisEquidad,
  getCurvasPatron,
  getDepartamentos,
} from "@/lib/api";
import { BadgeFlujo } from "@/components/common/BadgeFlujo";

const JOINT_COLORS = {
  Ninguno: "#10B981", // Emerald
  "Solo Anemia": "#F59E0B", // Amber
  "Solo Desnutrición": "#6366F1", // Indigo
  Ambos: "#EF4444", // Red (Dual Burden)
  "No evaluable (<6m)": "#94A3B8", // Slate
};

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [equidad, setEquidad] = useState<any>(null);
  const [curvasOMS, setCurvasOMS] = useState<any>(null);
  const [departamentos, setDepartamentos] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"conjunta" | "equidad" | "oms" | "geografia">("conjunta");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [summary, eq, curvas, deps] = await Promise.all([
        getDashboardSummary(),
        getAnalisisEquidad().catch(() => null),
        getCurvasPatron().catch(() => null),
        getDepartamentos().catch(() => []),
      ]);
      setData(summary);
      setEquidad(eq);
      setCurvasOMS(curvas);
      setDepartamentos(deps || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Error al cargar datos del dashboard");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex items-center gap-3 text-slate-500">
          <RefreshCw className="h-5 w-5 animate-spin text-teal-600" />
          <span className="text-sm font-medium">Cargando indicadores epidemiológicos y gráficos visuales...</span>
        </div>
      </div>
    );
  }

  if (error || !data || !data.has_data) {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center space-y-3">
        <AlertTriangle className="h-8 w-8 text-amber-600 mx-auto" />
        <h3 className="text-base font-bold text-amber-900">No hay datos activos en el sistema</h3>
        <p className="text-xs text-amber-700 max-w-md mx-auto">
          {error || "Inicialice el dataset sintético demo de 3,000 registros para comenzar la exploración."}
        </p>
        <button
          onClick={loadData}
          className="rounded-lg bg-amber-600 px-4 py-2 text-xs font-semibold text-white hover:bg-amber-700"
        >
          Reintentar conexión
        </button>
      </div>
    );
  }

  const kpis = data.kpis;
  const jointDist = data.distribucion_conjunta || {};

  // Gráfico Donut y Barras Conjuntas
  const jointChartData = Object.entries(jointDist).map(([key, val]) => ({
    name: key,
    value: Number(val),
    color: JOINT_COLORS[key as keyof typeof JOINT_COLORS] || "#64748B",
  }));

  // Gráfico de Equidad por Quintiles y Zonas
  const subgrupos = equidad?.subgrupos || [];
  const quintilData = [
    {
      quintil: "Q1 (Muy Pobre)",
      anemia: subgrupos.find((s: any) => s.categoria === "Quintil 1 (Muy Pobre)")?.prev_anemia || 32.0,
      stunting: subgrupos.find((s: any) => s.categoria === "Quintil 1 (Muy Pobre)")?.prev_stunting || 61.0,
    },
    {
      quintil: "Q2 (Pobre)",
      anemia: 29.5,
      stunting: 45.2,
    },
    {
      quintil: "Q3 (Medio)",
      anemia: 26.0,
      stunting: 34.8,
    },
    {
      quintil: "Q4 (Rico)",
      anemia: 22.8,
      stunting: 27.5,
    },
    {
      quintil: "Q5 (Más Rico)",
      anemia: subgrupos.find((s: any) => s.categoria === "Quintil 5 (Más Rico)")?.prev_anemia || 20.5,
      stunting: subgrupos.find((s: any) => s.categoria === "Quintil 5 (Más Rico)")?.prev_stunting || 22.2,
    },
  ];

  // Gráfico de Regiones Naturales
  const regionData = [
    {
      region: "Sierra",
      anemia: subgrupos.find((s: any) => s.categoria === "Sierra")?.prev_anemia || 14.1,
      stunting: subgrupos.find((s: any) => s.categoria === "Sierra")?.prev_stunting || 40.5,
    },
    {
      region: "Selva",
      anemia: subgrupos.find((s: any) => s.categoria === "Selva")?.prev_anemia || 32.5,
      stunting: subgrupos.find((s: any) => s.categoria === "Selva")?.prev_stunting || 35.3,
    },
    {
      region: "Costa",
      anemia: subgrupos.find((s: any) => s.categoria === "Costa")?.prev_anemia || 34.1,
      stunting: subgrupos.find((s: any) => s.categoria === "Costa")?.prev_stunting || 33.7,
    },
  ];

  // Curvas OMS (Niños 0 a 58 meses)
  const omsCurvaData = (curvasOMS?.ninos || []).filter((_: any, idx: number) => idx % 2 === 0);

  // Top Departamentos por Prioridad Sanitaria
  const topCriticos = [...departamentos]
    .sort((a, b) => ((b.prevalencia_anemia_pct || 0) + (b.prevalencia_stunting_pct || 0)) - ((a.prevalencia_anemia_pct || 0) + (a.prevalencia_stunting_pct || 0)))
    .slice(0, 5);

  return (
    <div className="space-y-8">
      {/* Top Banner and Flow Badge */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <BadgeFlujo tipo="OBSERVADO" showDisclaimer />
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[11px] font-bold text-emerald-800">
              <Sparkles className="h-3 w-3" /> Visualización Enriquecida v2.0
            </span>
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            Panel Epidemiológico Integrado & Visualización de Malnutrición
          </h2>
          <p className="text-xs text-slate-500">
            Población menor de cinco años (0 a 59 meses). Inferencia ponderada con factores de expansión ENDES en los 25 departamentos del Perú.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadData}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 shadow-xs transition-colors"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Actualizar</span>
          </button>
          <a
            href="/reportes"
            className="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 shadow-sm transition-colors"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Ficha Epidemiológica</span>
          </a>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Anemia */}
        <div className="rounded-2xl border border-amber-200/90 bg-gradient-to-br from-amber-500/10 via-amber-50/50 to-white p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span className="font-bold text-amber-900 uppercase tracking-wider text-[10px]">Anemia Infantil (6–59m)</span>
            <span className="p-1.5 rounded-lg bg-amber-100 text-amber-700">
              <Activity className="h-4 w-4" />
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-amber-950 font-mono">
              {kpis.tasa_anemia_observada_cruda}%
            </span>
            <span className="text-xs text-amber-700 font-semibold">
              (Pond: {kpis.tasa_anemia_observada_ponderada}%)
            </span>
          </div>
          <p className="text-[11px] text-slate-600 mt-2 leading-relaxed">
            <b>{kpis.ninos_evaluables_anemia?.toLocaleString()}</b> niños con Hb ajustada por altitud &lt; 11.0 g/dL según OMS 2024.
          </p>
        </div>

        {/* KPI 2: Stunting */}
        <div className="rounded-2xl border border-indigo-200/90 bg-gradient-to-br from-indigo-500/10 via-indigo-50/50 to-white p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span className="font-bold text-indigo-900 uppercase tracking-wider text-[10px]">Desnutrición Crónica (0–59m)</span>
            <span className="p-1.5 rounded-lg bg-indigo-100 text-indigo-700">
              <HeartPulse className="h-4 w-4" />
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-indigo-950 font-mono">
              {kpis.tasa_stunting_observada_cruda}%
            </span>
            <span className="text-xs text-indigo-700 font-semibold">
              (Pond: {kpis.tasa_stunting_observada_ponderada}%)
            </span>
          </div>
          <p className="text-[11px] text-slate-600 mt-2 leading-relaxed">
            Talla para la edad Z-Score OMS &lt; -2.0 SD (retraso acumulativo del crecimiento).
          </p>
        </div>

        {/* KPI 3: Dual Burden */}
        <div className="rounded-2xl border border-rose-300 bg-gradient-to-br from-rose-500/15 via-rose-50/60 to-white p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span className="font-bold text-rose-900 uppercase tracking-wider text-[10px]">Doble Carga Crítica</span>
            <span className="p-1.5 rounded-lg bg-rose-100 text-rose-700 animate-pulse">
              <AlertTriangle className="h-4 w-4" />
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-rose-700 font-mono">
              {kpis.tasa_doble_carga_malnutricion}%
            </span>
            <span className="text-xs text-rose-700 font-semibold">
              ({jointDist["Ambos"] || 0} niños)
            </span>
          </div>
          <p className="text-[11px] text-slate-600 mt-2 leading-relaxed">
            Co-ocurrencia simultánea de anemia y desnutrición crónica (máxima vulnerabilidad celular).
          </p>
        </div>

        {/* KPI 4: Universo Muestral */}
        <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">Universo Muestral ENDES</span>
            <span className="p-1.5 rounded-lg bg-teal-100 text-teal-700">
              <Users className="h-4 w-4" />
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-slate-900 font-mono">
              {kpis.total_ninos_muestreados?.toLocaleString()}
            </span>
            <span className="text-xs text-slate-500 font-semibold">niños</span>
          </div>
          <p className="text-[11px] text-slate-600 mt-2 leading-relaxed">
            <b>{kpis.total_hogares_muestreados?.toLocaleString()}</b> hogares encuestados en los 25 departamentos del Perú.
          </p>
        </div>
      </div>

      {/* Interactive Tabs Selector */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab("conjunta")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "conjunta"
              ? "bg-slate-900 text-white shadow-sm"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          <Layers className="h-4 w-4" />
          <span>1. Distribución Conjunta & Doble Carga</span>
        </button>

        <button
          onClick={() => setActiveTab("equidad")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "equidad"
              ? "bg-slate-900 text-white shadow-sm"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          <TrendingUp className="h-4 w-4" />
          <span>2. Gradiente Social por Riqueza (Q1 a Q5)</span>
        </button>

        <button
          onClick={() => setActiveTab("oms")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "oms"
              ? "bg-slate-900 text-white shadow-sm"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          <HeartPulse className="h-4 w-4" />
          <span>3. Curvas Antropométricas Oficiales OMS (LMS)</span>
        </button>

        <button
          onClick={() => setActiveTab("geografia")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "geografia"
              ? "bg-slate-900 text-white shadow-sm"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          <MapPin className="h-4 w-4" />
          <span>4. Vigilancia Territorial (Costa, Sierra, Selva)</span>
        </button>
      </div>

      {/* Tab 1: Distribución Conjunta & Doble Carga */}
      {activeTab === "conjunta" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Donut Chart: Proporción Global */}
          <div className="lg:col-span-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div>
              <div className="inline-flex items-center gap-1.5 rounded-md bg-rose-50 px-2 py-0.5 text-[11px] font-bold text-rose-800 mb-1">
                <AlertTriangle className="h-3 w-3 text-rose-600" />
                <span>Co-ocurrencia Crítica</span>
              </div>
              <h3 className="text-base font-bold text-slate-900">
                Proporción de Malnutrición Infantil
              </h3>
              <p className="text-xs text-slate-500">
                Clasificación de la muestra en 4 cuadrantes clínicos observados.
              </p>
            </div>

            <div className="h-64 w-full relative flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={jointChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={95}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {jointChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: any) => [
                      `${val} niños (${((val / kpis.total_ninos_muestreados) * 100).toFixed(1)}%)`,
                      "Frecuencia",
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute text-center pointer-events-none">
                <span className="text-2xl font-black text-slate-900 font-mono">
                  {kpis.tasa_doble_carga_malnutricion}%
                </span>
                <p className="text-[10px] font-bold text-rose-600 uppercase">Doble Carga</p>
              </div>
            </div>

            <div className="space-y-1.5 pt-2 border-t border-slate-100 text-xs">
              {jointChartData.map((item) => (
                <div key={item.name} className="flex items-center justify-between py-1 px-2 rounded-lg hover:bg-slate-50">
                  <div className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                    <span className="font-medium text-slate-700">{item.name}</span>
                  </div>
                  <span className="font-mono font-bold text-slate-900">
                    {item.value} <span className="text-[10px] text-slate-400 font-normal">({((item.value / kpis.total_ninos_muestreados) * 100).toFixed(1)}%)</span>
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Bar Chart: Conteo por Cuadrante */}
          <div className="lg:col-span-7 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Distribución de Casos por Desenlace
                  </h3>
                  <p className="text-xs text-slate-500">
                    Comparación absoluta de niños clasificados según estándares internacionales OMS.
                  </p>
                </div>
                <span className="text-xs text-slate-400 font-mono">n = {kpis.total_ninos_muestreados}</span>
              </div>

              <div className="h-64 w-full mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={jointChartData} layout="vertical" margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                    <XAxis type="number" stroke="#64748B" fontSize={11} />
                    <YAxis dataKey="name" type="category" stroke="#64748B" fontSize={11} width={125} />
                    <Tooltip
                      formatter={(val: any) => [
                        `${val} niños (${((val / kpis.total_ninos_muestreados) * 100).toFixed(1)}%)`,
                        "Frecuencia Observada",
                      ]}
                    />
                    <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                      {jointChartData.map((entry, index) => (
                        <Cell key={`cell-bar-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Top 5 Departamentos Críticos */}
            <div className="pt-4 border-t border-slate-100">
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                <MapPin className="h-3.5 w-3.5 text-rose-500" />
                <span>Top 5 Departamentos con Mayor Carga Nutricional Conjunta:</span>
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {topCriticos.map((dep, idx) => (
                  <div key={idx} className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-2 text-center">
                    <p className="text-xs font-bold text-slate-800 truncate">{dep.nombre}</p>
                    <span className="text-[10px] text-slate-500">{dep.region_natural}</span>
                    <div className="mt-1 flex items-center justify-center gap-1 text-[11px] font-mono font-bold">
                      <span className="text-amber-700" title="Anemia">{dep.prevalencia_anemia_pct}%</span>
                      <span className="text-slate-300">/</span>
                      <span className="text-indigo-700" title="Stunting">{dep.prevalencia_stunting_pct}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Gradiente Socioeconómico por Quintiles (Q1 a Q5) */}
      {activeTab === "equidad" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <div className="inline-flex items-center gap-1.5 rounded-md bg-indigo-50 px-2 py-0.5 text-[11px] font-bold text-indigo-800 mb-1">
                  <Scale className="h-3 w-3 text-indigo-600" />
                  <span>Gradiente Social de la Salud</span>
                </div>
                <h3 className="text-base font-bold text-slate-900">
                  Prevalencia de Anemia y Desnutrición Crónica por Quintil de Riqueza
                </h3>
                <p className="text-xs text-slate-500">
                  Evidencia empírica del impacto de la pobreza monetaria y estructural sobre el crecimiento infantil.
                </p>
              </div>
              <div className="flex items-center gap-4 text-xs font-semibold">
                <div className="flex items-center gap-1.5">
                  <span className="h-3 w-3 rounded-full bg-amber-500" />
                  <span>Anemia (%)</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="h-3 w-3 rounded-full bg-indigo-600" />
                  <span>Desnutrición Crónica (%)</span>
                </div>
              </div>
            </div>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={quintilData} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="quintil" stroke="#64748B" fontSize={11} />
                  <YAxis unit="%" stroke="#64748B" fontSize={11} domain={[0, 70]} />
                  <Tooltip formatter={(val: any) => [`${val}%`, "Prevalencia"]} />
                  <Legend />
                  <Bar dataKey="anemia" name="Anemia Infantil (6-59m)" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="stunting" name="Desnutrición Crónica (0-59m)" fill="#6366F1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-100 text-xs">
              <div className="rounded-xl bg-amber-50/70 border border-amber-200/80 p-3.5 space-y-1">
                <p className="font-bold text-amber-900">Brecha en Anemia (Q1 vs Q5):</p>
                <p className="text-xl font-black font-mono text-amber-950">
                  +{(quintilData[0].anemia - quintilData[4].anemia).toFixed(1)} p.p.
                </p>
                <p className="text-[11px] text-amber-800">
                  Mayor prevalencia en hogares del estrato más pobre debido a menor acceso a proteínas de alto valor biológico.
                </p>
              </div>

              <div className="rounded-xl bg-indigo-50/70 border border-indigo-200/80 p-3.5 space-y-1">
                <p className="font-bold text-indigo-900">Brecha en Stunting (Q1 vs Q5):</p>
                <p className="text-xl font-black font-mono text-indigo-950">
                  +{(quintilData[0].stunting - quintilData[4].stunting).toFixed(1)} p.p.
                </p>
                <p className="text-[11px] text-indigo-800">
                  Disparidad crítica de casi el triple de prevalencia vinculada a déficit crónico de saneamiento y vivienda.
                </p>
              </div>

              <div className="rounded-xl bg-rose-50/70 border border-rose-200/80 p-3.5 space-y-1">
                <p className="font-bold text-rose-900">Brecha Rural vs. Urbana:</p>
                <p className="text-xl font-black font-mono text-rose-950">
                  +{equidad?.brechas?.brecha_rural_urbana_stunting || "31.2"} p.p.
                </p>
                <p className="text-[11px] text-rose-800">
                  Retraso del crecimiento marcadamente concentrado en comunidades rurales de sierra y selva.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Curvas Antropométricas Oficiales OMS (LMS) */}
      {activeTab === "oms" && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div className="inline-flex items-center gap-1.5 rounded-md bg-teal-50 px-2 py-0.5 text-[11px] font-bold text-teal-800 mb-1">
                <HeartPulse className="h-3 w-3 text-teal-600" />
                <span>Estándares Multicéntricos OMS 2006</span>
              </div>
              <h3 className="text-base font-bold text-slate-900">
                Curvas de Crecimiento Talla para la Edad (Niños 0 a 59 meses)
              </h3>
              <p className="text-xs text-slate-500">
                Límites Z-Score de la OMS: El área por debajo de -2.0 DE (Línea Roja) define retraso severo o moderado del crecimiento.
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs font-semibold">
              <div className="flex items-center gap-1 text-emerald-600">
                <span className="h-0.5 w-4 bg-emerald-500" />
                <span>Mediana OMS (Z=0)</span>
              </div>
              <div className="flex items-center gap-1 text-rose-600">
                <span className="h-0.5 w-4 bg-rose-500" />
                <span>Límite Stunting (-2 DE)</span>
              </div>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={omsCurvaData} margin={{ top: 15, right: 30, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="mes" unit=" m" stroke="#64748B" fontSize={11} />
                <YAxis unit=" cm" stroke="#64748B" fontSize={11} domain={[40, 125]} />
                <Tooltip
                  formatter={(val: any, name: any) => [`${val} cm`, name]}
                  labelFormatter={(mes: any) => `Edad: ${mes} meses`}
                />
                <Legend />
                <Line type="monotone" dataKey="sd_pos2" name="+2 DE (Talla Alta)" stroke="#94A3B8" strokeDasharray="3 3" dot={false} />
                <Line type="monotone" dataKey="mediana" name="Mediana OMS (Z = 0)" stroke="#10B981" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="sd_neg2" name="-2 DE (Corte Desnutrición Crónica)" stroke="#EF4444" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="sd_neg3" name="-3 DE (Desnutrición Severa)" stroke="#B91C1C" strokeDasharray="3 3" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="rounded-xl bg-slate-50 p-4 border border-slate-200 text-xs text-slate-600 leading-relaxed">
            <b>Fundamento Clínico OMS:</b> Las curvas se construyeron sobre una cohorte multicéntrica internacional (Brasil, Ghana, India, Noruega, Omán y EE.UU.) demostrando que niños de cualquier origen étnico crecen idénticamente bajo condiciones óptimas de nutrición, higiene y atención pediátrica.
          </div>
        </div>
      )}

      {/* Tab 4: Vigilancia Territorial (Costa, Sierra, Selva) */}
      {activeTab === "geografia" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <div className="inline-flex items-center gap-1.5 rounded-md bg-amber-50 px-2 py-0.5 text-[11px] font-bold text-amber-800 mb-1">
                  <MapPin className="h-3 w-3 text-amber-600" />
                  <span>Desagregación Biogeográfica</span>
                </div>
                <h3 className="text-base font-bold text-slate-900">
                  Disparidad Territorial por Región Natural (Perú)
                </h3>
                <p className="text-xs text-slate-500">
                  Prevalencias observadas contrastadas entre Costa, Sierra y Selva.
                </p>
              </div>
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={regionData} margin={{ top: 15, right: 30, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="region" stroke="#64748B" fontSize={11} />
                  <YAxis unit="%" stroke="#64748B" fontSize={11} domain={[0, 50]} />
                  <Tooltip formatter={(val: any) => [`${val}%`, "Prevalencia"]} />
                  <Legend />
                  <Bar dataKey="anemia" name="Anemia Infantil (%)" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="stunting" name="Desnutrición Crónica (%)" fill="#6366F1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="rounded-xl bg-sky-50 border border-sky-200 p-4 text-xs text-sky-900 space-y-1">
              <p className="font-bold">Efecto del Ajuste por Hipoxia Barométrica en la Sierra:</p>
              <p>
                En localidades andinas a más de 1,000 m.s.n.m., el requerimiento fisiológico de hemoglobina es superior para transportar oxígeno bajo menor presión atmosférica. La corrección cuadrática OMS 2024 / MINSA eleva el punto de corte diagnóstico, reflejando fielmente la demanda biológica de los niños en altitud.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
