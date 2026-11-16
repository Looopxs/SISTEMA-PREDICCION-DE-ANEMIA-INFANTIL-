"use client";

import React, { useState, useEffect } from "react";
import {
  Activity,
  HeartPulse,
  Calculator,
  Info,
  CheckCircle2,
  AlertTriangle,
  Scale,
  Ruler,
  Mountain,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceDot,
} from "recharts";
import { evaluarAntropometria, getCurvasPatron } from "@/lib/api";
import { BadgeFlujo } from "@/components/common/BadgeFlujo";

export default function AntropometriaPage() {
  const [formData, setFormData] = useState({
    edad_meses: 24,
    sexo: "M",
    talla_cm: 82.5,
    peso_kg: 11.5,
    hemoglobina_g_dl: 10.4,
    altitud_msnm: 2325,
  });

  const [resultado, setResultado] = useState<any>(null);
  const [curvas, setCurvas] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCurvasPatron().then((data) => setCurvas(data));
    handleCalcular();
  }, []);

  const handleCalcular = async () => {
    setLoading(true);
    try {
      const res = await evaluarAntropometria(formData);
      setResultado(res);
    } catch (err: any) {
      alert("Error en cálculo: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = curvas
    ? formData.sexo === "M"
      ? curvas.ninos
      : curvas.ninas
    : [];

  return (
    <div className="space-y-8">
      {/* Header and Flow Distinction Badge */}
      <div className="border-b border-slate-200 pb-5 space-y-2">
        <BadgeFlujo tipo="OBSERVADO" showDisclaimer />
        <h2 className="text-2xl font-black text-slate-900 mt-2">
          Análisis Antropométrico y Clasificación Oficial de Hemoglobina
        </h2>
        <p className="text-xs text-slate-500">
          Cálculo determinístico sin modelos de machine learning. Aplicación estricta de directrices OMS 2024 para anemia
          y Patrones de Crecimiento OMS 2006 (HAZ/WAZ/WHZ).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Input Form (4 cols) */}
        <div className="lg:col-span-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-5">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Calculator className="h-5 w-5 text-brand-600" />
            <h3 className="text-base font-bold text-slate-900">
              Datos Antropométricos y de Laboratorio
            </h3>
          </div>

          <div className="space-y-4 text-xs">
            {/* Age & Sex */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Edad (meses)</label>
                <input
                  type="number"
                  min="0"
                  max="59"
                  value={formData.edad_meses}
                  onChange={(e) => setFormData({ ...formData, edad_meses: parseInt(e.target.value) || 0 })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-900 font-mono font-bold focus:border-brand-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Sexo Biológico</label>
                <select
                  value={formData.sexo}
                  onChange={(e) => setFormData({ ...formData, sexo: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-900 font-bold focus:border-brand-500 focus:outline-hidden"
                >
                  <option value="M">Masculino (Niño)</option>
                  <option value="F">Femenino (Niña)</option>
                </select>
              </div>
            </div>

            {/* Height & Weight */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-bold text-slate-700 block mb-1 flex items-center gap-1">
                  <Ruler className="h-3.5 w-3.5 text-indigo-600" />
                  <span>Talla / Longitud (cm)</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="35"
                  max="130"
                  value={formData.talla_cm}
                  onChange={(e) => setFormData({ ...formData, talla_cm: parseFloat(e.target.value) || 0 })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-900 font-mono font-bold focus:border-brand-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1 flex items-center gap-1">
                  <Scale className="h-3.5 w-3.5 text-teal-600" />
                  <span>Peso (kg)</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="2"
                  max="40"
                  value={formData.peso_kg}
                  onChange={(e) => setFormData({ ...formData, peso_kg: parseFloat(e.target.value) || 0 })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-900 font-mono font-bold focus:border-brand-500 focus:outline-hidden"
                />
              </div>
            </div>

            {/* Hemoglobin & Altitude */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-bold text-slate-700 block mb-1 flex items-center gap-1">
                  <Activity className="h-3.5 w-3.5 text-amber-600" />
                  <span>Hb Observada (g/dL)</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="3"
                  max="25"
                  value={formData.hemoglobina_g_dl}
                  onChange={(e) => setFormData({ ...formData, hemoglobina_g_dl: parseFloat(e.target.value) || 0 })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-900 font-mono font-bold focus:border-brand-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1 flex items-center gap-1">
                  <Mountain className="h-3.5 w-3.5 text-slate-600" />
                  <span>Altitud (msnm)</span>
                </label>
                <input
                  type="number"
                  min="0"
                  max="5200"
                  value={formData.altitud_msnm}
                  onChange={(e) => setFormData({ ...formData, altitud_msnm: parseFloat(e.target.value) || 0 })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-900 font-mono font-bold focus:border-brand-500 focus:outline-hidden"
                />
              </div>
            </div>

            <button
              onClick={handleCalcular}
              disabled={loading}
              className="w-full rounded-xl bg-brand-600 py-3 text-xs font-bold text-white shadow-md hover:bg-brand-700 transition"
            >
              {loading ? "Calculando..." : "Evaluar Mediciones Clínicas"}
            </button>
          </div>
        </div>

        {/* Right Column: Clinical Classification Results & Growth Chart (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {resultado && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Anemia Card */}
              <div className="rounded-2xl border border-amber-200 bg-amber-50/40 p-5 space-y-2">
                <span className="text-[10px] uppercase font-bold tracking-wider text-amber-800">
                  Clasificación de Hemoglobina
                </span>
                <div className="text-xl font-black text-amber-950">
                  {resultado.anemia_severidad === "Normal" ? "Sin Anemia" : `Anemia ${resultado.anemia_severidad}`}
                </div>
                <div className="text-xs space-y-1 text-slate-700 pt-1 border-t border-amber-200/60 font-mono">
                  <p>Hb Observada: <b>{resultado.hemoglobina_observada} g/dL</b></p>
                  <p>Factor Altitud ({formData.altitud_msnm}m): <b>-{resultado.factor_ajuste_altitud} g/dL</b></p>
                  <p className="font-bold text-amber-900">Hb Ajustada: {resultado.hemoglobina_ajustada} g/dL</p>
                </div>
                <span className="text-[10px] text-slate-500 block pt-1">
                  Umbral OMS: &lt;11.0 g/dL en 6-59 meses
                </span>
              </div>

              {/* Stunting Card */}
              <div className="rounded-2xl border border-indigo-200 bg-indigo-50/40 p-5 space-y-2">
                <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-800">
                  Índice Talla para la Edad (HAZ)
                </span>
                <div className="text-xl font-black text-indigo-950">
                  {resultado.stunting_severidad === "Normal" ? "Crecimiento Normal" : `Desnutrición Crónica ${resultado.stunting_severidad}`}
                </div>
                <div className="text-xs space-y-1 text-slate-700 pt-1 border-t border-indigo-200/60 font-mono">
                  <p>Z-Score Talla/Edad (HAZ): <b>{resultado.haz} SD</b></p>
                  <p>Z-Score Peso/Edad (WAZ): <b>{resultado.waz} SD</b></p>
                  <p>Z-Score Peso/Talla (WHZ): <b>{resultado.whz} SD</b></p>
                </div>
                <span className="text-[10px] text-slate-500 block pt-1">
                  Umbral OMS: &lt; -2.0 SD (Retraso de crecimiento)
                </span>
              </div>
            </div>
          )}

          {/* Growth Curve Chart */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-900">
                Curvas de Crecimiento Infantil OMS 2006 (Talla / Edad) — {formData.sexo === "M" ? "Niños" : "Niñas"}
              </h3>
              <span className="text-[10px] text-slate-400 font-mono">0 a 59 meses</span>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis dataKey="mes" fontSize={10} stroke="#94A3B8" />
                  <YAxis domain={[40, 125]} fontSize={10} stroke="#94A3B8" />
                  <Tooltip formatter={(val: any) => [`${val} cm`]} />
                  <Line type="monotone" dataKey="sd_pos3" stroke="#CBD5E1" dot={false} strokeDasharray="2 2" name="+3 SD" />
                  <Line type="monotone" dataKey="sd_pos2" stroke="#94A3B8" dot={false} strokeDasharray="2 2" name="+2 SD" />
                  <Line type="monotone" dataKey="mediana" stroke="#10B981" strokeWidth={2} dot={false} name="Mediana OMS" />
                  <Line type="monotone" dataKey="sd_neg2" stroke="#EF4444" strokeWidth={2} dot={false} name="-2 SD (Umbral Stunting)" />
                  <Line type="monotone" dataKey="sd_neg3" stroke="#991B1B" dot={false} strokeDasharray="2 2" name="-3 SD (Severo)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

