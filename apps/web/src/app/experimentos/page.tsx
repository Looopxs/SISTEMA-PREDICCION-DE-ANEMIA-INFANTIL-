"use client";

import React, { useEffect, useState } from "react";
import {
  BrainCircuit,
  Play,
  RotateCcw,
  CheckCircle2,
  Clock,
  Terminal,
  Layers,
  Sparkles,
  AlertCircle,
} from "lucide-react";
import { getExperimentos, createExperimento, runExperimento, getDatasets } from "@/lib/api";

export default function ExperimentosPage() {
  const [experimentos, setExperimentos] = useState<any[]>([]);
  const [datasets, setDatasets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningId, setRunningId] = useState<string | null>(null);

  // New experiment form state
  const [nombre, setNombre] = useState("Estudio Comparativo M1-M5 (Conglomerados)");
  const [semilla, setSemilla] = useState(42);
  const [particion, setParticion] = useState("Estratificada por Conglomerados (PSU)");

  const loadData = async () => {
    try {
      const exps = await getExperimentos();
      setExperimentos(exps);
      const ds = await getDatasets();
      setDatasets(ds);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Polling for progress
    return () => clearInterval(interval);
  }, []);

  const handleCreateAndRun = async () => {
    if (datasets.length === 0) {
      alert("Primero debe cargar un dataset en la sección Datasets.");
      return;
    }
    try {
      const newExp = await createExperimento({
        dataset_id: datasets[0].id,
        nombre: nombre,
        semilla_random: semilla,
        particion_tipo: particion,
        train_pct: 0.7,
        val_pct: 0.15,
        test_pct: 0.15,
      });
      await runExperimento(newExp.id);
      setRunningId(newExp.id);
      await loadData();
    } catch (err: any) {
      alert("Error al iniciar experimento: " + err.message);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b border-slate-200 pb-5">
        <h2 className="text-2xl font-black text-slate-900">
          Laboratorio de Entrenamiento Experimental (M1 – M5)
        </h2>
        <p className="text-xs text-slate-500">
          Entrenamiento reproducible de baselines independientes, red neuronal multitarea (M4) y meta-modelo híbrido (M5).
        </p>
      </div>

      {/* Launcher Card */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <BrainCircuit className="h-5 w-5 text-brand-600" />
            <h3 className="text-base font-bold text-slate-900">Configuración de Nuevo Protocolo Experimental</h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400">Zero Leakage Guaranteed</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div>
            <label className="font-bold text-slate-700 block mb-1">Nombre del Estudio</label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-900 font-medium focus:border-brand-500 focus:outline-hidden"
            />
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">Estrategia de Partición</label>
            <select
              value={particion}
              onChange={(e) => setParticion(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-900 font-medium focus:border-brand-500 focus:outline-hidden"
            >
              <option value="Estratificada por Conglomerados (PSU)">Estratificada por Conglomerados (PSU ENDES)</option>
              <option value="Partición Temporal">Partición Temporal (Años base / test)</option>
              <option value="Partición Geográfica">Partición Geográfica (Holdout Regional)</option>
            </select>
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">Semilla Aleatoria (Reproducibilidad)</label>
            <input
              type="number"
              value={semilla}
              onChange={(e) => setSemilla(parseInt(e.target.value) || 42)}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-900 font-mono font-bold focus:border-brand-500 focus:outline-hidden"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          <p className="text-[11px] text-slate-500">
            Se entrenarán <b>M1 (Logística)</b>, <b>M2 (Random Forest)</b>, <b>M3 (CatBoost)</b>, <b>M4 (Multi-Task NN)</b> y <b>M5 (MTL + XGBoost)</b>.
          </p>

          <button
            onClick={handleCreateAndRun}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-ai-600 px-5 py-2.5 text-xs font-bold text-white shadow-sm hover:from-brand-700 hover:to-ai-700 transition"
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            <span>Ejecutar Protocolo M1–M5</span>
          </button>
        </div>
      </div>

      {/* Experiments History List */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-slate-900">Historial de Experimentos</h3>

        <div className="space-y-4">
          {experimentos.map((exp) => (
            <div
              key={exp.id}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-4"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-slate-900">{exp.nombre}</h4>
                    <span
                      className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                        exp.estado === "completado"
                          ? "bg-emerald-100 text-emerald-800"
                          : exp.estado === "en_progreso"
                          ? "bg-ai-100 text-ai-800 animate-pulse"
                          : "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {exp.estado === "completado" ? "Completado" : exp.estado === "en_progreso" ? "En Progreso" : exp.estado}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{exp.descripcion}</p>
                </div>

                <div className="flex items-center gap-3 text-xs text-slate-500 font-mono">
                  <span>Partición: {exp.particion_tipo}</span>
                  <span>Semilla: {exp.semilla_random}</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-[11px] font-mono text-slate-500">
                  <span>Progreso de Entrenamiento</span>
                  <span>{exp.progreso_pct}%</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full bg-gradient-to-r from-brand-500 to-ai-600 transition-all duration-500"
                    style={{ width: `${exp.progreso_pct}%` }}
                  />
                </div>
              </div>

              {/* Logs terminal box */}
              {exp.logs_sanitizados && (
                <div className="rounded-xl bg-slate-950 p-4 font-mono text-[11px] text-slate-300 leading-relaxed max-h-48 overflow-y-auto">
                  <div className="flex items-center gap-1.5 text-slate-500 pb-2 border-b border-slate-800 text-[10px] uppercase font-bold">
                    <Terminal className="h-3.5 w-3.5" />
                    <span>Bitácora de Ejecución Sanitizada</span>
                  </div>
                  <pre className="whitespace-pre-wrap mt-2">{exp.logs_sanitizados}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

