"use client";

import React, { useEffect, useState } from "react";
import { ShieldCheck, AlertCircle, FileCheck2, Filter, Info, BarChart2 } from "lucide-react";
import { getDatasets, getDatasetQuality } from "@/lib/api";

export default function CalidadDatosPage() {
  const [quality, setQuality] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDatasets().then((dsList) => {
      if (dsList.length > 0) {
        getDatasetQuality(dsList[0].id).then((q) => {
          setQuality(q);
          setLoading(false);
        });
      } else {
        setLoading(false);
      }
    });
  }, []);

  if (loading) {
    return <div className="p-12 text-center text-xs text-slate-400">Cargando diagnóstico de calidad...</div>;
  }

  if (!quality) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-xs text-slate-500">
        No se encontró dataset cargado para evaluación de calidad. Ingrese a la sección de Datasets y cargue la demo.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b border-slate-200 pb-5">
        <h2 className="text-2xl font-black text-slate-900">Control de Calidad, Integridad y Linaje</h2>
        <p className="text-xs text-slate-500">
          Auditoría de consistencia de rangos, tratamiento de faltantes y elegibilidad de microdatos.
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">Registros con Anemia Evaluable</span>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {quality.registros_validos_anemia?.toLocaleString()} / {quality.total_registros?.toLocaleString()}
          </div>
          <span className="text-[11px] text-amber-700 bg-amber-50 px-2 py-0.5 rounded font-medium mt-2 inline-block">
            {((quality.registros_validos_anemia / quality.total_registros) * 100).toFixed(1)}% elegibles (&ge;6m)
          </span>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">Registros con Desnutrición Evaluable</span>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {quality.registros_validos_stunting?.toLocaleString()} / {quality.total_registros?.toLocaleString()}
          </div>
          <span className="text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-medium mt-2 inline-block">
            {((quality.registros_validos_stunting / quality.total_registros) * 100).toFixed(1)}% evaluables (0–59m)
          </span>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">Tratamiento de Ponderaciones</span>
          <div className="text-2xl font-black text-brand-700 mt-1">
            Muestreo Complejo
          </div>
          <span className="text-[11px] text-slate-500 mt-2 block">
            Factor de expansión aplicado a conglomerados PSU.
          </span>
        </div>
      </div>

      {/* Age eligibility breakdown */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
        <h3 className="text-base font-bold text-slate-900">
          Distribución por Grupos de Edad y Elegibilidad Oficial
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Grupo Etario</th>
                <th className="px-4 py-3">N Muestral</th>
                <th className="px-4 py-3">Elegibilidad Anemia (OMS 2024)</th>
                <th className="px-4 py-3">Prevalencia Anemia (%)</th>
                <th className="px-4 py-3">Prevalencia Desnutrición (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(quality.distribucion_edades || []).map((g: any, idx: number) => (
                <tr key={idx} className="hover:bg-slate-50/50">
                  <td className="px-4 py-2.5 font-bold text-slate-800">{g.grupo_etario}</td>
                  <td className="px-4 py-2.5 font-mono">{g.n}</td>
                  <td className="px-4 py-2.5">
                    {g.prevalencia_anemia !== null ? (
                      <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded text-[10px] font-bold">
                        Elegible
                      </span>
                    ) : (
                      <span className="text-slate-500 bg-slate-100 px-2 py-0.5 rounded text-[10px] font-bold">
                        No evaluable (&lt;6m)
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 font-mono font-bold text-amber-700">
                    {g.prevalencia_anemia !== null ? `${g.prevalencia_anemia}%` : "—"}
                  </td>
                  <td className="px-4 py-2.5 font-mono font-bold text-indigo-700">
                    {g.prevalencia_stunting}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

