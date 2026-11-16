"use client";

import React, { useState, useEffect } from "react";
import { getDepartamentos, getAnalisisEquidad } from "@/lib/api";
import {
  MapPin,
  AlertTriangle,
  TrendingUp,
  Activity,
  Layers,
  ArrowUpDown,
  Filter,
  ShieldAlert,
  Info,
  Scale,
  BarChart2,
  Table as TableIcon,
  Sparkles,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

const REGION_COLORS: Record<string, string> = {
  Costa: "#0284C7", // Sky blue
  Sierra: "#D97706", // Amber
  Selva: "#059669", // Emerald
};

export default function GeografiaPage() {
  const [departamentos, setDepartamentos] = useState<any[]>([]);
  const [equidad, setEquidad] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<string>("TODAS");
  const [sortBy, setSortBy] = useState<"nombre" | "anemia" | "desnutricion" | "total">("anemia");
  const [sortAsc, setSortAsc] = useState<boolean>(false);
  const [visualMode, setVisualMode] = useState<"grafico" | "tabla">("grafico");

  useEffect(() => {
    Promise.all([getDepartamentos(), getAnalisisEquidad()])
      .then(([deps, eq]) => {
        setDepartamentos(deps || []);
        setEquidad(eq || null);
      })
      .catch((err) => {
        console.error("Error cargando datos geográficos:", err);
        setError("Error al cargar la información departamental y brechas de equidad.");
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredDeps = (departamentos || [])
    .filter((d) => selectedRegion === "TODAS" || d.region_natural === selectedRegion)
    .sort((a, b) => {
      let valA: any =
        sortBy === "anemia"
          ? a.prevalencia_anemia_pct ?? 0
          : sortBy === "desnutricion"
          ? a.prevalencia_stunting_pct ?? 0
          : sortBy === "total"
          ? a.n_muestral ?? 0
          : a.nombre ?? "";
      let valB: any =
        sortBy === "anemia"
          ? b.prevalencia_anemia_pct ?? 0
          : sortBy === "desnutricion"
          ? b.prevalencia_stunting_pct ?? 0
          : sortBy === "total"
          ? b.n_muestral ?? 0
          : b.nombre ?? "";

      if (typeof valA === "string") {
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return sortAsc ? valA - valB : valB - valA;
    });

  // Datos para gráfico de barras horizontal de 25 departamentos
  const barDepsData = [...filteredDeps].map((d) => ({
    nombre: d.nombre,
    anemia: Number((d.prevalencia_anemia_pct ?? 0).toFixed(1)),
    stunting: Number((d.prevalencia_stunting_pct ?? 0).toFixed(1)),
    region: d.region_natural,
    color: REGION_COLORS[d.region_natural] || "#64748B",
  }));

  // Extraer subgrupos de forma segura
  const subgrupos = equidad?.subgrupos || [];
  const brechas = equidad?.brechas || {};

  const findSubgrupo = (cat: string) => subgrupos.find((s: any) => s.categoria === cat);

  const ruralData = findSubgrupo("Rural");
  const urbanData = findSubgrupo("Urbana");
  const q1Data = findSubgrupo("Quintil 1 (Muy Pobre)");
  const q5Data = findSubgrupo("Quintil 5 (Más Rico)");
  const sierraData = findSubgrupo("Sierra");
  const selvaData = findSubgrupo("Selva");
  const costaData = findSubgrupo("Costa");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center gap-1 rounded-full bg-teal-100 px-2.5 py-0.5 text-[11px] font-bold text-teal-800">
              <MapPin className="h-3 w-3" /> Vigilancia Territorial Oficial
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            Módulo 7: Vigilancia Territorial y Brechas de Equidad (25 Departamentos)
          </h1>
          <p className="text-sm text-muted-foreground">
            Monitoreo epidemiológico desagregado en los 25 departamentos del Perú y análisis de gradientes de desigualdad social.
          </p>
        </div>

        {/* Visual Switcher */}
        <div className="flex items-center gap-1.5 bg-muted p-1 rounded-xl">
          <button
            onClick={() => setVisualMode("grafico")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              visualMode === "grafico" ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <BarChart2 className="h-3.5 w-3.5" />
            <span>Gráfico Comparativo</span>
          </button>
          <button
            onClick={() => setVisualMode("tabla")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              visualMode === "tabla" ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <TableIcon className="h-3.5 w-3.5" />
            <span>Tabla de Microdatos</span>
          </button>
        </div>
      </div>

      {/* Alerta de Diseño Complejo ENDES */}
      <div className="p-4 bg-sky-50 dark:bg-sky-950/30 border border-sky-200 dark:border-sky-900 rounded-xl flex items-start gap-3">
        <Info className="h-5 w-5 text-sky-600 dark:text-sky-400 shrink-0 mt-0.5" />
        <div className="text-xs text-sky-900 dark:text-sky-200 space-y-1">
          <p className="font-bold">Advertencia de Inferencia Muestral ENDES:</p>
          <p>
            El diseño muestral polietápico y estratificado por conglomerados de ENDES garantiza representatividad a nivel nacional, departamental y por área de residencia. <strong>No está diseñado para estimaciones distritales directas</strong> sin técnicas formales de estimación en áreas pequeñas (SAE). NutriPredict AI respeta este límite y no extrapola microdatos a niveles sub-departamentales no calibrados.
          </p>
        </div>
      </div>

      {/* Indicadores de Brechas de Equidad */}
      {equidad && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Brecha Rural vs Urbano */}
          <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Gradiente Rural / Urbano
              </span>
              <Scale className="h-4 w-4 text-primary" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span>Anemia Rural:</span>
                <span className="font-bold font-mono text-foreground">
                  {ruralData?.prev_anemia != null ? `${ruralData.prev_anemia.toFixed(1)}%` : "N/D"}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span>Anemia Urbana:</span>
                <span className="font-bold font-mono text-foreground">
                  {urbanData?.prev_anemia != null ? `${urbanData.prev_anemia.toFixed(1)}%` : "N/D"}
                </span>
              </div>
              <div className="pt-2 border-t border-border flex items-center justify-between text-xs text-rose-600 dark:text-rose-400 font-semibold">
                <span>Brecha Absoluta (Rural - Urbano):</span>
                <span>
                  {brechas.brecha_rural_urbana_anemia != null
                    ? `${brechas.brecha_rural_urbana_anemia > 0 ? "+" : ""}${brechas.brecha_rural_urbana_anemia.toFixed(1)} p.p.`
                    : "N/D"}
                </span>
              </div>
            </div>
          </div>

          {/* Brecha Quintil 1 vs Quintil 5 */}
          <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Brecha Riqueza (Q1 vs Q5)
              </span>
              <TrendingUp className="h-4 w-4 text-rose-500" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span>Stunting Q1 (Muy Pobre):</span>
                <span className="font-bold font-mono text-foreground">
                  {q1Data?.prev_stunting != null ? `${q1Data.prev_stunting.toFixed(1)}%` : "N/D"}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span>Stunting Q5 (Más Rico):</span>
                <span className="font-bold font-mono text-foreground">
                  {q5Data?.prev_stunting != null ? `${q5Data.prev_stunting.toFixed(1)}%` : "N/D"}
                </span>
              </div>
              <div className="pt-2 border-t border-border flex items-center justify-between text-xs text-rose-600 dark:text-rose-400 font-semibold">
                <span>Brecha Absoluta (Q1 - Q5):</span>
                <span>
                  {brechas.brecha_socioeconomica_q1_q5_stunting != null
                    ? `${brechas.brecha_socioeconomica_q1_q5_stunting > 0 ? "+" : ""}${brechas.brecha_socioeconomica_q1_q5_stunting.toFixed(1)} p.p.`
                    : "N/D"}
                </span>
              </div>
            </div>
          </div>

          {/* Brecha por Región Natural */}
          <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Disparidad Geográfica
              </span>
              <MapPin className="h-4 w-4 text-amber-500" />
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex items-center justify-between">
                <span>Sierra (Anemia):</span>
                <span className="font-bold font-mono text-foreground">
                  {sierraData?.prev_anemia != null ? `${sierraData.prev_anemia.toFixed(1)}%` : "N/D"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Selva (Anemia):</span>
                <span className="font-bold font-mono text-foreground">
                  {selvaData?.prev_anemia != null ? `${selvaData.prev_anemia.toFixed(1)}%` : "N/D"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Costa (Anemia):</span>
                <span className="font-bold font-mono text-foreground">
                  {costaData?.prev_anemia != null ? `${costaData.prev_anemia.toFixed(1)}%` : "N/D"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Controles de Filtro y Orden */}
      <div className="bg-card border border-border rounded-xl p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-xs font-semibold text-muted-foreground">Filtrar por Región:</span>
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="text-xs bg-background border border-border rounded-md px-2.5 py-1.5 font-medium text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="TODAS">Todas las Regiones (25 Departamentos)</option>
            <option value="Costa">Costa</option>
            <option value="Sierra">Sierra</option>
            <option value="Selva">Selva</option>
          </select>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          <span className="text-xs font-semibold text-muted-foreground">Ordenar por:</span>
          <select
            value={sortBy}
            onChange={(e: any) => setSortBy(e.target.value)}
            className="text-xs bg-background border border-border rounded-md px-2.5 py-1.5 font-medium text-foreground"
          >
            <option value="anemia">Prevalencia de Anemia</option>
            <option value="desnutricion">Prevalencia Desnutrición</option>
            <option value="total">Muestra Evaluada (n)</option>
            <option value="nombre">Nombre Departamento</option>
          </select>
          <button
            onClick={() => setSortAsc(!sortAsc)}
            className="p-1.5 rounded-md border border-border hover:bg-secondary text-muted-foreground"
            title="Invertir orden"
          >
            <ArrowUpDown className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Gráfico Horizontal de los 25 Departamentos */}
      {visualMode === "grafico" && (
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="text-base font-bold text-foreground">
                Ranking Departamental de Prevalencia de Anemia (%)
              </h3>
              <p className="text-xs text-muted-foreground">
                Desagregación en los 25 departamentos del Perú con código de color por región natural (Línea roja: Promedio Nacional 26.1%).
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs font-semibold">
              <div className="flex items-center gap-1">
                <span className="h-3 w-3 rounded-full bg-sky-500" />
                <span>Costa</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="h-3 w-3 rounded-full bg-amber-500" />
                <span>Sierra</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="h-3 w-3 rounded-full bg-emerald-500" />
                <span>Selva</span>
              </div>
            </div>
          </div>

          <div className="h-[650px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={barDepsData}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 40, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" unit="%" stroke="#64748B" fontSize={11} domain={[0, 50]} />
                <YAxis dataKey="nombre" type="category" stroke="#64748B" fontSize={11} width={120} />
                <Tooltip
                  formatter={(val: any, name: any, item: any) => [
                    `${val}% (${item.payload.region})`,
                    "Tasa de Anemia",
                  ]}
                />
                <ReferenceLine x={26.1} stroke="#EF4444" strokeWidth={2} strokeDasharray="4 4" label={{ value: "Promedio Nacional (26.1%)", position: "top", fill: "#EF4444", fontSize: 10 }} />
                <Bar dataKey="anemia" radius={[0, 4, 4, 0]}>
                  {barDepsData.map((entry, index) => (
                    <Cell key={`cell-dep-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Tabla Departamental de 25 Departamentos */}
      {visualMode === "tabla" && (
        <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <MapPin className="h-4 w-4 text-primary" />
              Tabla Epidemiológica Departamental (Perú)
            </h2>
            <span className="text-xs text-muted-foreground">
              Mostrando {filteredDeps.length} de 25 departamentos
            </span>
          </div>

          {loading ? (
            <div className="p-12 text-center text-xs text-muted-foreground flex items-center justify-center gap-2">
              <Activity className="h-4 w-4 animate-spin text-primary" />
              Cargando estadísticas territoriales...
            </div>
          ) : error ? (
            <div className="p-8 text-center text-xs text-destructive">{error}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-border bg-muted/40 text-muted-foreground font-semibold">
                    <th className="p-3">Departamento</th>
                    <th className="p-3">Región Natural</th>
                    <th className="p-3">Altitud Media</th>
                    <th className="p-3 text-right">Muestra (n)</th>
                    <th className="p-3 text-right">Tasa Anemia (%)</th>
                    <th className="p-3 text-right">Tasa Desnutrición Crónica (%)</th>
                    <th className="p-3 text-center">Prioridad Sanitaria</th>
                    <th className="p-3 text-center">Estado Muestral</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredDeps.map((dep, idx) => {
                    const isSmallSample = dep.muestra_insuficiente || (dep.n_muestral != null && dep.n_muestral < 30);
                    const prevAnemia = dep.prevalencia_anemia_pct ?? 0;
                    const prevStunting = dep.prevalencia_stunting_pct ?? 0;

                    return (
                      <tr key={idx} className="hover:bg-muted/20 transition-colors">
                        <td className="p-3 font-semibold text-foreground">{dep.nombre}</td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-secondary text-secondary-foreground">
                            {dep.region_natural}
                          </span>
                        </td>
                        <td className="p-3 font-mono text-muted-foreground">
                          {dep.altitud_msnm != null ? `${Math.round(dep.altitud_msnm)} m` : "—"}
                        </td>
                        <td className="p-3 text-right font-mono font-medium text-foreground">
                          {dep.n_muestral ?? 0}
                        </td>
                        <td className="p-3 text-right">
                          <span
                            className={`font-mono font-bold px-2 py-0.5 rounded ${
                              prevAnemia > 40
                                ? "bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-300"
                                : prevAnemia > 25
                                ? "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300"
                                : "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300"
                            }`}
                          >
                            {prevAnemia.toFixed(1)}%
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <span
                            className={`font-mono font-bold px-2 py-0.5 rounded ${
                              prevStunting > 20
                                ? "bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-300"
                                : prevStunting > 10
                                ? "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300"
                                : "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300"
                            }`}
                          >
                            {prevStunting.toFixed(1)}%
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              dep.prioridad_sanitaria === "Muy Alta"
                                ? "bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-300"
                                : dep.prioridad_sanitaria === "Alta"
                                ? "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300"
                                : "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300"
                            }`}
                          >
                            {dep.prioridad_sanitaria || "Moderada"}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          {isSmallSample ? (
                            <span
                              className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-700 bg-amber-100 dark:bg-amber-950/40 dark:text-amber-300 px-2 py-0.5 rounded"
                              title="Muestra insuficiente para estimaciones estables (n < 30)"
                            >
                              <AlertTriangle className="h-3 w-3" />
                              n &lt; 30 (Alerta)
                            </span>
                          ) : (
                            <span className="text-[10px] text-muted-foreground font-mono">Válida</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
