"use client";

import React, { useState, useEffect } from "react";
import { BadgeFlujo } from "@/components/common/BadgeFlujo";
import { predecirRiesgoIndividual, getModelos } from "@/lib/api";
import {
  Brain,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Sparkles,
  Info,
  TrendingUp,
  Activity,
  Layers,
  Award,
} from "lucide-react";

const DEPARTAMENTOS_PERU = [
  { nombre: "Amazonas", region: "Selva", alt: 2335 },
  { nombre: "Áncash", region: "Sierra", alt: 3052 },
  { nombre: "Apurímac", region: "Sierra", alt: 2378 },
  { nombre: "Arequipa", region: "Costa", alt: 2335 },
  { nombre: "Ayacucho", region: "Sierra", alt: 2761 },
  { nombre: "Cajamarca", region: "Sierra", alt: 2750 },
  { nombre: "Callao", region: "Costa", alt: 5 },
  { nombre: "Cusco", region: "Sierra", alt: 3399 },
  { nombre: "Huancavelica", region: "Sierra", alt: 3676 },
  { nombre: "Huánuco", region: "Sierra", alt: 1880 },
  { nombre: "Ica", region: "Costa", alt: 406 },
  { nombre: "Junín", region: "Sierra", alt: 3271 },
  { nombre: "La Libertad", region: "Costa", alt: 34 },
  { nombre: "Lambayeque", region: "Costa", alt: 18 },
  { nombre: "Lima", region: "Costa", alt: 154 },
  { nombre: "Loreto", region: "Selva", alt: 106 },
  { nombre: "Madre de Dios", region: "Selva", alt: 183 },
  { nombre: "Moquegua", region: "Costa", alt: 1410 },
  { nombre: "Pasco", region: "Sierra", alt: 4330 },
  { nombre: "Piura", region: "Costa", alt: 29 },
  { nombre: "Puno", region: "Sierra", alt: 3827 },
  { nombre: "San Martín", region: "Selva", alt: 350 },
  { nombre: "Tacna", region: "Costa", alt: 562 },
  { nombre: "Tumbes", region: "Costa", alt: 6 },
  { nombre: "Ucayali", region: "Selva", alt: 154 },
];

export default function PrediccionesPage() {
  const [modelos, setModelos] = useState<any[]>([]);
  const [selectedModeloId, setSelectedModeloId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<any | null>(null);

  // Formulario strictly pre-measurement (Zero Data Leakage)
  const [formData, setFormData] = useState({
    departamento: "Puno",
    region_natural: "Sierra",
    altitud_msnm: 3827,
    area_residencia: "Rural",
    edad_meses: 18,
    sexo: "M",
    quintil_riqueza: 1,
    edad_madre: 22,
    educacion_madre: "Primaria",
    controles_prenatales: 3,
    orden_nacimiento: 2,
    piso_tierra: true,
    agua_red: false,
    saneamiento_red: false,
    lactancia_actual: true,
    suplemento_hierro: false,
  });

  useEffect(() => {
    getModelos()
      .then((mods) => {
        setModelos(mods);
        if (mods.length > 0) {
          // Select M5 or M4 by default if available
          const m5 = mods.find((m) => m.codigo === "M5");
          const m4 = mods.find((m) => m.codigo === "M4");
          setSelectedModeloId(m5 ? m5.id : m4 ? m4.id : mods[0].id);
        }
      })
      .catch((err) => console.error("Error cargando modelos:", err));
  }, []);

  const handleDeptChange = (deptName: string) => {
    const found = DEPARTAMENTOS_PERU.find((d) => d.nombre === deptName);
    if (found) {
      setFormData((prev) => ({
        ...prev,
        departamento: found.nombre,
        region_natural: found.region,
        altitud_msnm: found.alt,
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await predecirRiesgoIndividual(formData, selectedModeloId || undefined);
      setResultado(res);
    } catch (err: any) {
      setError(err.message || "Error al calcular la predicción de riesgo");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Encabezado con Diferenciación de Flujo */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              Módulo 5: Inferencia Multisalida Pre-Medición
            </h1>
            <BadgeFlujo tipo="B" />
          </div>
          <p className="text-sm text-muted-foreground">
            Estimación simultánea de probabilidades de riesgo para Anemia Infantil y Desnutrición Crónica utilizando únicamente covariables socioeconómicas, maternas y de entorno previas a la toma física de muestras.
          </p>
        </div>

        {/* Selector de Modelo */}
        <div className="flex items-center gap-2 bg-card border border-border p-2 rounded-lg">
          <Layers className="h-4 w-4 text-primary" />
          <span className="text-xs font-semibold text-muted-foreground">Modelo IA:</span>
          <select
            value={selectedModeloId}
            onChange={(e) => setSelectedModeloId(e.target.value)}
            className="text-xs bg-background border border-border rounded px-2 py-1 font-medium text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            {modelos.map((m) => (
              <option key={m.id} value={m.id}>
                {m.codigo} — {m.nombre} ({m.familia})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Alerta de Cero Fuga de Datos (Zero Data Leakage) */}
      <div className="p-3.5 bg-sky-50 dark:bg-sky-950/30 border border-sky-200 dark:border-sky-900 rounded-lg flex items-start gap-3">
        <Info className="h-5 w-5 text-sky-600 dark:text-sky-400 shrink-0 mt-0.5" />
        <div className="text-xs text-sky-900 dark:text-sky-200">
          <span className="font-bold">Garantía Metodológica de Cero Fuga de Datos (Zero Data Leakage):</span> Este formulario 
          excluye por diseño cualquier medición física (hemoglobina, talla, z-score HAZ, peso). El objetivo es pronosticar el perfil de vulnerabilidad antes de que el personal de salud llegue al hogar o realice un tamizaje invasivo.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Formulario de Covariables Pre-Medición (7 columnas) */}
        <div className="lg:col-span-7 bg-card border border-border rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-border">
            <h2 className="text-base font-semibold text-foreground flex items-center gap-2">
              <Brain className="h-4 w-4 text-primary" />
              Determinantes Previos a la Medición (X_pre)
            </h2>
            <span className="text-[11px] bg-secondary text-secondary-foreground px-2 py-0.5 rounded font-mono">
              16 Factores
            </span>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Ubicación y Entorno */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                1. Contexto Territorial y Geográfico
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Departamento</label>
                  <select
                    value={formData.departamento}
                    onChange={(e) => handleDeptChange(e.target.value)}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  >
                    {DEPARTAMENTOS_PERU.map((d) => (
                      <option key={d.nombre} value={d.nombre}>
                        {d.nombre}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Área</label>
                  <select
                    value={formData.area_residencia}
                    onChange={(e) => setFormData({ ...formData, area_residencia: e.target.value })}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  >
                    <option value="Urbano">Urbano</option>
                    <option value="Rural">Rural</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Altitud (m.s.n.m.)</label>
                  <input
                    type="number"
                    value={formData.altitud_msnm}
                    onChange={(e) => setFormData({ ...formData, altitud_msnm: Number(e.target.value) })}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  />
                </div>
              </div>
            </div>

            {/* Datos del Niño */}
            <div className="pt-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                2. Características del Niño(a)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Edad (meses)</label>
                  <input
                    type="number"
                    min="0"
                    max="59"
                    value={formData.edad_meses}
                    onChange={(e) => setFormData({ ...formData, edad_meses: Number(e.target.value) })}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  />
                  <span className="text-[10px] text-muted-foreground">0 a 59 meses</span>
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Sexo</label>
                  <select
                    value={formData.sexo}
                    onChange={(e) => setFormData({ ...formData, sexo: e.target.value })}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  >
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Orden Nacimiento</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={formData.orden_nacimiento}
                    onChange={(e) => setFormData({ ...formData, orden_nacimiento: Number(e.target.value) })}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  />
                </div>
              </div>
            </div>

            {/* Características Maternas y del Hogar */}
            <div className="pt-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                3. Factores Maternos y Socioeconómicos
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Quintil de Riqueza</label>
                  <select
                    value={formData.quintil_riqueza}
                    onChange={(e) => setFormData({ ...formData, quintil_riqueza: Number(e.target.value) })}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  >
                    <option value="1">Q1 (Muy Pobre)</option>
                    <option value="2">Q2 (Pobre)</option>
                    <option value="3">Q3 (Medio)</option>
                    <option value="4">Q4 (Rico)</option>
                    <option value="5">Q5 (Muy Rico)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Edad de la Madre</label>
                  <input
                    type="number"
                    min="12"
                    max="50"
                    value={formData.edad_madre}
                    onChange={(e) => setFormData({ ...formData, edad_madre: Number(e.target.value) })}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Nivel Educativo Madre</label>
                  <select
                    value={formData.educacion_madre}
                    onChange={(e) => setFormData({ ...formData, educacion_madre: e.target.value })}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  >
                    <option value="Sin educacion">Sin educación</option>
                    <option value="Primaria">Primaria</option>
                    <option value="Secundaria">Secundaria</option>
                    <option value="Superior">Superior</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1">Controles Prenatales (APN)</label>
                  <input
                    type="number"
                    min="0"
                    max="20"
                    value={formData.controles_prenatales}
                    onChange={(e) => setFormData({ ...formData, controles_prenatales: Number(e.target.value) })}
                    className="w-full text-xs bg-background border border-border rounded-md p-2"
                  />
                </div>
                <div className="sm:col-span-2 flex items-center gap-4 pt-3">
                  <label className="flex items-center gap-2 cursor-pointer text-xs">
                    <input
                      type="checkbox"
                      checked={formData.piso_tierra}
                      onChange={(e) => setFormData({ ...formData, piso_tierra: e.target.checked })}
                      className="rounded border-border text-primary"
                    />
                    Piso de tierra en vivienda
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer text-xs">
                    <input
                      type="checkbox"
                      checked={formData.agua_red}
                      onChange={(e) => setFormData({ ...formData, agua_red: e.target.checked })}
                      className="rounded border-border text-primary"
                    />
                    Agua por red pública
                  </label>
                </div>
              </div>
            </div>

            {/* Alimentación y Cuidado */}
            <div className="pt-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                4. Nutrición y Prácticas de Cuidado
              </h3>
              <div className="flex flex-wrap items-center gap-6">
                <label className="flex items-center gap-2 cursor-pointer text-xs">
                  <input
                    type="checkbox"
                    checked={formData.lactancia_actual}
                    onChange={(e) => setFormData({ ...formData, lactancia_actual: e.target.checked })}
                    className="rounded border-border text-primary"
                  />
                  Lactancia materna actual
                </label>
                <label className="flex items-center gap-2 cursor-pointer text-xs">
                  <input
                    type="checkbox"
                    checked={formData.suplemento_hierro}
                    onChange={(e) => setFormData({ ...formData, suplemento_hierro: e.target.checked })}
                    className="rounded border-border text-primary"
                  />
                  Suplemento de hierro (gotas / jarabe / multimicronutrientes)
                </label>
              </div>
            </div>

            <div className="pt-4 flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="w-full sm:w-auto px-6 py-2.5 bg-primary text-primary-foreground font-semibold text-xs rounded-lg hover:bg-primary/90 transition-colors shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Activity className="h-4 w-4 animate-spin" />
                    Procesando Inferencia Multisalida...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Calcular Probabilidades de Riesgo (IA)
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Panel de Resultados y Perfil de Vulnerabilidad (5 columnas) */}
        <div className="lg:col-span-5 space-y-5">
          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 text-destructive text-xs rounded-lg flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {resultado ? (
            <div className="space-y-4">
              {/* Tarjeta de Riesgos Conjuntos */}
              <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-border pb-3">
                  <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-primary" />
                    Probabilidades Estimadas de Riesgo
                  </h3>
                  <span className="text-[10px] font-mono bg-primary/10 text-primary px-2 py-0.5 rounded">
                    {resultado.modelo_codigo}
                  </span>
                </div>

                {/* Matriz 2D de Cuadrantes de Riesgo Multitarea */}
                <div className="rounded-xl border border-border bg-card p-4 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-foreground flex items-center gap-1.5">
                      <Sparkles className="h-3.5 w-3.5 text-primary" />
                      Posicionamiento en Matriz de Riesgo 2D
                    </span>
                    <span className="text-[10px] text-muted-foreground font-mono">
                      ({(resultado.probabilidad_anemia * 100).toFixed(0)}%, {(resultado.probabilidad_desnutricion * 100).toFixed(0)}%)
                    </span>
                  </div>

                  <div className="relative h-48 w-full rounded-lg border border-border/80 overflow-hidden bg-background">
                    {/* Cuadrantes de Fondo */}
                    <div className="absolute inset-0 grid grid-cols-2 grid-rows-2">
                      {/* Cuadrante Superior Izquierdo: Solo Desnutrición */}
                      <div className="bg-indigo-500/10 border-r border-b border-dashed border-border/60 flex items-start justify-start p-2">
                        <span className="text-[9px] font-bold text-indigo-700 uppercase">Solo Desnutrición</span>
                      </div>
                      {/* Cuadrante Superior Derecho: Doble Carga */}
                      <div className="bg-rose-500/15 border-b border-dashed border-border/60 flex items-start justify-end p-2">
                        <span className="text-[9px] font-bold text-rose-700 uppercase">Doble Carga Crítica</span>
                      </div>
                      {/* Cuadrante Inferior Izquierdo: Bajo Riesgo */}
                      <div className="bg-emerald-500/10 border-r border-dashed border-border/60 flex items-end justify-start p-2">
                        <span className="text-[9px] font-bold text-emerald-700 uppercase">Bajo Riesgo</span>
                      </div>
                      {/* Cuadrante Inferior Derecho: Solo Anemia */}
                      <div className="bg-amber-500/10 flex items-end justify-end p-2">
                        <span className="text-[9px] font-bold text-amber-700 uppercase">Solo Anemia</span>
                      </div>
                    </div>

                    {/* Líneas de Corte Umbral (50% Anemia, 40% Desnutrición) */}
                    <div className="absolute left-1/2 top-0 bottom-0 w-px bg-slate-400/40 border-dashed" />
                    <div className="absolute top-[60%] left-0 right-0 h-px bg-slate-400/40 border-dashed" />

                    {/* Punto Pulsante del Niño Evaluado */}
                    <div
                      className="absolute z-20 transition-all duration-700 ease-out flex items-center justify-center -translate-x-1/2 -translate-y-1/2"
                      style={{
                        left: `${Math.max(8, Math.min(92, resultado.probabilidad_anemia * 100))}%`,
                        top: `${Math.max(8, Math.min(92, 100 - resultado.probabilidad_desnutricion * 100))}%`,
                      }}
                    >
                      <div className="relative">
                        <span className="absolute -inset-2 rounded-full bg-rose-500/40 animate-ping" />
                        <div className="h-5 w-5 rounded-full bg-rose-600 border-2 border-white shadow-md flex items-center justify-center text-[9px] text-white font-black">
                          ●
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-muted-foreground px-1">
                    <span>← Menor Riesgo Anemia</span>
                    <span className="font-semibold text-foreground">Eje X: Prob. Anemia | Eje Y: Prob. Stunting</span>
                    <span>Mayor Riesgo Anemia →</span>
                  </div>
                </div>

                {/* Anemia */}
                <div className="space-y-1.5 p-3 rounded-lg border border-border bg-background">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-foreground">Riesgo de Anemia Infantil</span>
                    <span className="font-mono font-bold text-sm text-foreground">
                      {(resultado.probabilidad_anemia * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        resultado.probabilidad_anemia > 0.5 ? "bg-amber-500" : "bg-emerald-500"
                      }`}
                      style={{ width: `${resultado.probabilidad_anemia * 100}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1">
                    <span>Nivel de Riesgo por Umbral:</span>
                    <span
                      className={`font-semibold px-2 py-0.5 rounded ${
                        resultado.riesgo_anemia === "Alto" || resultado.clasificacion_anemia
                          ? "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300"
                          : "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300"
                      }`}
                    >
                      {resultado.riesgo_anemia || (resultado.clasificacion_anemia ? "Alerta de Alto Riesgo" : "Bajo Riesgo")}
                    </span>
                  </div>
                </div>

                {/* Desnutrición Crónica (Stunting) */}
                <div className="space-y-1.5 p-3 rounded-lg border border-border bg-background">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-foreground">Riesgo de Desnutrición Crónica</span>
                    <span className="font-mono font-bold text-sm text-foreground">
                      {(resultado.probabilidad_desnutricion * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        resultado.probabilidad_desnutricion > 0.4 ? "bg-rose-500" : "bg-emerald-500"
                      }`}
                      style={{ width: `${resultado.probabilidad_desnutricion * 100}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1">
                    <span>Nivel de Riesgo por Umbral:</span>
                    <span
                      className={`font-semibold px-2 py-0.5 rounded ${
                        resultado.riesgo_desnutricion === "Alto" || resultado.clasificacion_desnutricion
                          ? "bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-300"
                          : "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300"
                      }`}
                    >
                      {resultado.riesgo_desnutricion || (resultado.clasificacion_desnutricion ? "Alerta de Alto Riesgo" : "Bajo Riesgo")}
                    </span>
                  </div>
                </div>

                {/* Perfil de Doble Carga / Vulnerabilidad */}
                <div className="p-3.5 rounded-lg border border-border bg-secondary/30">
                  <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                    Perfil de Vulnerabilidad Multitarea
                  </div>
                  <div className="text-sm font-bold text-foreground mb-1">
                    {resultado.riesgo_conjunto_categorizado || resultado.perfil_vulnerabilidad}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {resultado.advertencia_cientifica || resultado.interpretacion_clinica}
                  </p>
                </div>
              </div>

              {/* Explicabilidad Local (Factores SHAP más influyentes) */}
              {(resultado.explicacion_shap?.factores_principales || resultado.factores_principales) && (
                <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
                  <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5">
                    <Award className="h-4 w-4 text-primary" />
                    Determinantes Locales Más Influyentes (SHAP)
                  </h4>
                  <div className="space-y-2">
                    {(resultado.explicacion_shap?.factores_principales || resultado.factores_principales || []).map((factor: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between text-xs p-2 rounded bg-background border border-border">
                        <span className="font-medium text-foreground">{factor.feature || factor.caracteristica}</span>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[11px] text-muted-foreground">
                            {(factor.impacto ?? factor.impacto_shap) > 0 ? `+${(factor.impacto ?? factor.impacto_shap).toFixed(3)}` : (factor.impacto ?? factor.impacto_shap).toFixed(3)}
                          </span>
                          <span
                            className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                              (factor.impacto ?? factor.impacto_shap) > 0
                                ? "bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300"
                                : "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                            }`}
                          >
                            {(factor.impacto ?? factor.impacto_shap) > 0 ? "Aumenta riesgo" : "Protector"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-card border border-dashed border-border rounded-xl p-8 text-center space-y-3">
              <div className="mx-auto w-12 h-12 rounded-full bg-secondary flex items-center justify-center text-muted-foreground">
                <Brain className="h-6 w-6" />
              </div>
              <h3 className="text-sm font-semibold text-foreground">Esperando Datos de Entrada</h3>
              <p className="text-xs text-muted-foreground max-w-xs mx-auto">
                Complete el formulario con los determinantes demográficos y presione &quot;Calcular Probabilidades de Riesgo&quot; para ejecutar la inferencia multitarea.
              </p>
            </div>
          )}

          {/* Descargo de Responsabilidad Científica */}
          <div className="p-3.5 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 rounded-lg flex items-start gap-3">
            <ShieldAlert className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-900 dark:text-amber-200">
              <span className="font-bold">Advertencia Ética y Epidemiológica:</span> NutriPredict AI es una herramienta de 
              vigilancia poblacional y priorización en campo. No emite diagnósticos médicos automáticos ni reemplaza la valoración integral por personal de salud.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

