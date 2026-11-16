"use client";

import React, { useEffect, useState } from "react";
import {
  Database,
  Upload,
  RefreshCw,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  Table as TableIcon,
  Eye,
  Download,
  Info,
} from "lucide-react";
import { getDatasets, seedDemoDataset, getDatasetPreview, getDatasetQuality } from "@/lib/api";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [qualityData, setQualityData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [activeTab, setActiveTab] = useState<"preview" | "quality">("preview");

  const loadDatasets = async () => {
    setLoading(true);
    try {
      const list = await getDatasets();
      setDatasets(list);
      if (list.length > 0 && !selectedDatasetId) {
        setSelectedDatasetId(list[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      getDatasetPreview(selectedDatasetId).then((res) => setPreviewData(res.data || []));
      getDatasetQuality(selectedDatasetId).then((res) => setQualityData(res));
    }
  }, [selectedDatasetId]);

  const handleSeedDemo = async () => {
    setSeeding(true);
    try {
      await seedDemoDataset();
      await loadDatasets();
    } catch (err: any) {
      alert("Error al cargar demo: " + err.message);
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h2 className="text-2xl font-black text-slate-900">Gestión de Fuentes y Datasets</h2>
          <p className="text-xs text-slate-500">
            Microdatos ENDES (INEI Perú), DHS Program e indicadores agregados UNICEF/WHO/World Bank JME.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSeedDemo}
            disabled={seeding}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-teal-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:from-brand-700 hover:to-teal-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${seeding ? "animate-spin" : ""}`} />
            <span>{seeding ? "Generando 3,000 casos..." : "Cargar Demo Sintética (3k niños)"}</span>
          </button>
        </div>
      </div>

      {/* Datasets Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {datasets.map((ds) => {
          const isSelected = ds.id === selectedDatasetId;
          return (
            <div
              key={ds.id}
              onClick={() => setSelectedDatasetId(ds.id)}
              className={`cursor-pointer rounded-2xl border p-5 transition-all shadow-xs ${
                isSelected
                  ? "border-brand-600 bg-brand-50/30 ring-1 ring-brand-500"
                  : "border-slate-200 bg-white hover:border-slate-300"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <Database className="h-4 w-4 text-brand-600" />
                  <span className="text-xs font-bold text-slate-700">{ds.origen}</span>
                </div>
                {ds.es_sintetico ? (
                  <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-bold text-amber-800">
                    Sintético Demo
                  </span>
                ) : (
                  <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] font-bold text-emerald-800">
                    Oficial
                  </span>
                )}
              </div>

              <h3 className="mt-3 text-sm font-bold text-slate-900">{ds.nombre}</h3>
              <p className="mt-1 text-xs text-slate-500 line-clamp-2">{ds.descripcion}</p>

              <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-[11px] text-slate-500">
                <span>Año: <b>{ds.anio}</b></span>
                <span>Registros: <b>{ds.total_registros?.toLocaleString()}</b></span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Detail / Preview Tabs */}
      {selectedDatasetId && (
        <div className="rounded-2xl border border-slate-200 bg-white shadow-xs overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-3 bg-slate-50/50">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab("preview")}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition ${
                  activeTab === "preview"
                    ? "bg-white text-slate-900 shadow-xs border border-slate-200"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                <TableIcon className="h-3.5 w-3.5 text-brand-600" />
                <span>Vista Previa de Microdatos</span>
              </button>
              <button
                onClick={() => setActiveTab("quality")}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition ${
                  activeTab === "quality"
                    ? "bg-white text-slate-900 shadow-xs border border-slate-200"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                <span>Diagnóstico de Calidad y Faltantes</span>
              </button>
            </div>

            <span className="text-xs text-slate-400">
              Mostrando primeros 20 registros
            </span>
          </div>

          {activeTab === "preview" ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100/70 text-slate-700 font-bold border-b border-slate-200">
                  <tr>
                    <th className="px-4 py-3">ID Niño</th>
                    <th className="px-4 py-3">Edad (m)</th>
                    <th className="px-4 py-3">Sexo</th>
                    <th className="px-4 py-3">Depto / Región</th>
                    <th className="px-4 py-3">Área</th>
                    <th className="px-4 py-3">Altitud</th>
                    <th className="px-4 py-3">Quintil</th>
                    <th className="px-4 py-3 bg-amber-50 text-amber-900">Hb Obs.</th>
                    <th className="px-4 py-3 bg-amber-50 text-amber-900">Hb Ajust.</th>
                    <th className="px-4 py-3 bg-amber-50 text-amber-900">Anemia</th>
                    <th className="px-4 py-3 bg-indigo-50 text-indigo-900">Talla (cm)</th>
                    <th className="px-4 py-3 bg-indigo-50 text-indigo-900">HAZ</th>
                    <th className="px-4 py-3 bg-indigo-50 text-indigo-900">Stunting</th>
                    <th className="px-4 py-3">Diagnóstico Conjunto</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                  {previewData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/80">
                      <td className="px-4 py-2 font-bold text-slate-800">{row.nino_id}</td>
                      <td className="px-4 py-2">{row.edad_meses}</td>
                      <td className="px-4 py-2">{row.sexo}</td>
                      <td className="px-4 py-2 font-sans">{row.departamento}</td>
                      <td className="px-4 py-2 font-sans">{row.area}</td>
                      <td className="px-4 py-2">{row.altitud_msnm}m</td>
                      <td className="px-4 py-2">Q{row.quintil_riqueza}</td>
                      <td className="px-4 py-2 bg-amber-50/40 text-amber-900 font-bold">
                        {row.hb_observada ?? "N/A"}
                      </td>
                      <td className="px-4 py-2 bg-amber-50/40 text-amber-900 font-bold">
                        {row.hb_ajustada ?? "N/A"}
                      </td>
                      <td className="px-4 py-2 bg-amber-50/40">
                        <span className={`px-1.5 py-0.5 rounded font-sans text-[10px] font-bold ${
                          row.anemia_observada === "Sí" ? "bg-amber-200 text-amber-900" : "bg-emerald-100 text-emerald-800"
                        }`}>
                          {row.anemia_observada}
                        </span>
                      </td>
                      <td className="px-4 py-2 bg-indigo-50/40 text-indigo-900 font-bold">{row.talla_cm}</td>
                      <td className="px-4 py-2 bg-indigo-50/40 text-indigo-900 font-bold">{row.haz}</td>
                      <td className="px-4 py-2 bg-indigo-50/40">
                        <span className={`px-1.5 py-0.5 rounded font-sans text-[10px] font-bold ${
                          row.desnutricion_cronica === "Sí" ? "bg-rose-200 text-rose-900" : "bg-emerald-100 text-emerald-800"
                        }`}>
                          {row.desnutricion_cronica}
                        </span>
                      </td>
                      <td className="px-4 py-2 font-sans text-slate-700">{row.estado_conjunto}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6 space-y-6">
              {qualityData ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <h4 className="text-sm font-bold text-slate-900">Cobertura y Completitud de Variables</h4>
                    <div className="space-y-2 text-xs">
                      {Object.entries(qualityData.cobertura_variables || {}).map(([key, val]: any) => (
                        <div key={key} className="flex items-center justify-between border-b border-slate-100 pb-1">
                          <span className="font-mono text-slate-600">{key}</span>
                          <span className="font-bold text-slate-900">{val}%</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-sm font-bold text-slate-900">Reglas y Advertencias Epidemiológicas</h4>
                    <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 space-y-2">
                      {(qualityData.advertencias || []).map((adv: string, idx: number) => (
                        <p key={idx} className="text-xs text-amber-800 flex items-start gap-2">
                          <Info className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                          <span>{adv}</span>
                        </p>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-400">Cargando reporte de calidad...</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

