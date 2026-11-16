"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  HeartPulse,
  BrainCircuit,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Database,
  BarChart3,
  Network,
  Globe2,
  FileText,
  Activity,
  Layers,
  CheckCircle2,
  Lock,
} from "lucide-react";

const CRISP_PHASES = [
  {
    fase: 1,
    nombre: "Comprensión del Problema",
    descripcion: "Definición de desenlaces conjuntos: Anemia infantil y Desnutrición crónica (stunting). Formulación de hipótesis de representaciones compartidas.",
    estado: "Completado",
    artefactos: "Pregunta científica, protocolo de evaluación sin fugas",
  },
  {
    fase: 2,
    nombre: "Comprensión de los Datos",
    descripcion: "Estructura ENDES/DHS, diseño muestral complejo (PSU y estratos), elegibilidad etaria (6–59m anemia vs 0–59m stunting).",
    estado: "Completado",
    artefactos: "Diccionario canónico, evaluación de faltantes y pesos",
  },
  {
    fase: 3,
    nombre: "Preparación de Datos",
    descripcion: "Partición por conglomerados PSU, normalización de covariables pre-medición, aislamiento estricto de Hb y HAZ como desenlaces.",
    estado: "Completado",
    artefactos: "Pipeline antifuga, matrices numéricas escaladas",
  },
  {
    fase: 4,
    nombre: "Modelado Científico (M1–M5)",
    descripcion: "Entrenamiento de baselines independientes (M1, M2, M3), Deep Multi-Task Learning (M4) e Híbrido Residual M4+XGBoost (M5).",
    estado: "Completado",
    artefactos: "5 familias de modelos, artefactos persistidos",
  },
  {
    fase: 5,
    nombre: "Evaluación Rigurosa",
    descripcion: "ROC-AUC, PR-AUC, F1, Brier Score, calibración ECE, prueba pareada de McNemar, bootstrap 1,000 iteraciones y negative transfer check.",
    estado: "Completado",
    artefactos: "Tablas comparativas, curvas ROC/PR, confiabilidad",
  },
  {
    fase: 6,
    nombre: "Despliegue y Vigilancia",
    descripcion: "Inferencia pre-medición, explicación con SHAP, análisis territorial y exportación de reportes científicos en PDF y Excel.",
    estado: "Operativo",
    artefactos: "Dashboard web, API REST, reportes descargables",
  },
];

const MODULE_CARDS = [
  {
    href: "/dashboard",
    title: "1. Dashboard Epidemiológico",
    desc: "Prevalencias observadas ponderadas, distribución conjunta de ambos desenlaces y filtros sociodemográficos.",
    icon: Activity,
    color: "from-teal-500 to-emerald-600",
  },
  {
    href: "/datasets",
    title: "2. Gestión de Datasets",
    desc: "Importación de microdatos ENDES/DHS, control de linaje, checksum e inspección de variables.",
    icon: Database,
    color: "from-blue-500 to-indigo-600",
  },
  {
    href: "/antropometria",
    title: "3. Antropometría y Hemoglobina",
    desc: "Flujo clínico determinístico: cálculo de HAZ/WAZ/WHZ según OMS 2006 y corrección de Hb por altitud OMS 2024.",
    icon: HeartPulse,
    color: "from-rose-500 to-pink-600",
  },
  {
    href: "/experimentos",
    title: "4. Laboratorio M1–M5",
    desc: "Entrenamiento experimental reproducible con partición estratificada por PSU y seguimiento en vivo.",
    icon: BrainCircuit,
    color: "from-purple-500 to-ai-600",
  },
  {
    href: "/predicciones",
    title: "5. Inferencia de Riesgo (IA)",
    desc: "Predicción probabilística con covariables pre-medición únicamente, perfil conjunto y umbrales óptimos.",
    icon: Sparkles,
    color: "from-amber-500 to-orange-600",
  },
  {
    href: "/explicabilidad",
    title: "6. Explicabilidad SHAP",
    desc: "Importancia de determinantes, gráficos beeswarm y factores waterfall individuales (asociación, no causalidad).",
    icon: Network,
    color: "from-cyan-500 to-teal-600",
  },
  {
    href: "/geografia",
    title: "7. Geografía y Equidad",
    desc: "Distribución por los 25 departamentos del Perú y brechas de equidad rural/urbana, sexo y nivel socioeconómico.",
    icon: Globe2,
    color: "from-emerald-500 to-teal-700",
  },
  {
    href: "/estadistica",
    title: "8. Laboratorio Estadístico",
    desc: "Pruebas pareadas de McNemar, curvas de calibración ECE, e intervalos de confianza empíricos al 95%.",
    icon: BarChart3,
    color: "from-indigo-500 to-violet-700",
  },
  {
    href: "/reportes",
    title: "9. Reportes PDF y Excel",
    desc: "Generación y descarga de informes científicos ejecutivos y libros de datos multi-hoja auditables.",
    icon: FileText,
    color: "from-slate-600 to-slate-800",
  },
];

export default function HomePage() {
  const [selectedPhase, setSelectedPhase] = useState(CRISP_PHASES[0]);

  return (
    <div className="space-y-10 pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-teal-950 p-8 md:p-12 text-white shadow-xl">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-teal-500/30 bg-teal-500/10 px-3.5 py-1 text-xs font-semibold text-teal-300 backdrop-blur-md">
            <Sparkles className="h-3.5 w-3.5" />
            <span>INV-02 · Inteligencia Artificial Explicable y Salud Pública</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-black tracking-tight leading-tight">
            Predicción Conjunta de <span className="text-teal-400">Anemia Infantil</span> y{" "}
            <span className="text-indigo-400">Desnutrición Crónica</span>
          </h1>
          <p className="text-sm md:text-base text-slate-300 leading-relaxed font-normal">
            Plataforma científica para investigar si el <b>Aprendizaje Multitarea (Multi-Task Learning)</b> aprovecha
            representaciones compartidas frente a modelos independientes, respetando el diseño complejo de la encuesta
            ENDES Perú y garantizando la <b>ausencia total de fuga de datos (Data Leakage)</b>.
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-xl bg-teal-500 px-5 py-3 text-sm font-bold text-slate-950 shadow-lg hover:bg-teal-400 transition"
            >
              <span>Explorar Dashboard</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/predicciones"
              className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-5 py-3 text-sm font-semibold text-white backdrop-blur-md hover:bg-white/20 transition"
            >
              <Sparkles className="h-4 w-4 text-indigo-300" />
              <span>Simulador de Inferencia Pre-Test</span>
            </Link>
            <Link
              href="/modelos"
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-slate-800/80 px-5 py-3 text-sm font-semibold text-slate-300 hover:text-white transition"
            >
              <span>Comparativa M1–M5</span>
            </Link>
          </div>
        </div>

        {/* Scientific Guarantees Pill */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-3 border-t border-slate-700/60 pt-6 text-xs">
          <div className="flex items-start gap-2.5">
            <Lock className="h-4 w-4 text-teal-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-white block">Zero Data Leakage</span>
              <span className="text-slate-400">Hb y talla jamás ingresan al conjunto de predictores X.</span>
            </div>
          </div>
          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="h-4 w-4 text-indigo-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-white block">Cinco Arquitecturas Reales</span>
              <span className="text-slate-400">M1 Logística, M2 RF, M3 CatBoost, M4 MTL y M5 Híbrido.</span>
            </div>
          </div>
          <div className="flex items-start gap-2.5">
            <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-white block">Apoyo a Vigilancia — No Clínico</span>
              <span className="text-slate-400">Estimación poblacional; no sustituye juicio médico.</span>
            </div>
          </div>
        </div>
      </section>

      {/* 9 Modules Grid */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Módulos del Sistema NutriPredict AI</h2>
            <p className="text-xs text-slate-500">
              Arquitectura modular integral de los 9 componentes solicitados en la especificación científica.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {MODULE_CARDS.map((m) => {
            const Icon = m.icon;
            return (
              <Link
                key={m.href}
                href={m.href}
                className="group relative flex flex-col justify-between rounded-2xl border border-slate-200/90 bg-white p-5 shadow-xs hover:border-brand-500 hover:shadow-md transition-all duration-200"
              >
                <div className="space-y-3">
                  <div className={`inline-flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${m.color} text-white shadow-sm`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-base font-bold text-slate-900 group-hover:text-brand-600 transition">
                    {m.title}
                  </h3>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    {m.desc}
                  </p>
                </div>
                <div className="mt-4 flex items-center gap-1 text-xs font-semibold text-brand-600 group-hover:translate-x-1 transition-transform">
                  <span>Ingresar al módulo</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* CRISP-DM Pipeline Interactive Stepper */}
      <section className="rounded-3xl border border-slate-200 bg-white p-6 md:p-8 shadow-xs space-y-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-brand-600 font-mono">
            Ciclo Metodológico Completo
          </span>
          <h2 className="text-xl font-bold text-slate-900">Flujo CRISP-DM Trazable</h2>
          <p className="text-xs text-slate-500">
            Cada fase implementada con entradas, salidas, evidencia científica y reproducibilidad garantizada.
          </p>
        </div>

        {/* Phase Buttons */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
          {CRISP_PHASES.map((p) => (
            <button
              key={p.fase}
              onClick={() => setSelectedPhase(p)}
              className={`flex flex-col items-start rounded-xl p-3 text-left transition border ${
                selectedPhase.fase === p.fase
                  ? "border-brand-600 bg-brand-50/70 text-brand-900 shadow-xs"
                  : "border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100"
              }`}
            >
              <span className="text-[10px] font-bold text-slate-400">FASE {p.fase}</span>
              <span className="text-xs font-bold truncate w-full">{p.nombre}</span>
              <span className="mt-1 text-[9px] font-semibold text-emerald-700 bg-emerald-100/80 px-1.5 py-0.5 rounded">
                {p.estado}
              </span>
            </button>
          ))}
        </div>

        {/* Selected Phase Detail Card */}
        <div className="rounded-2xl border border-brand-200 bg-brand-50/40 p-5 space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">
              Fase {selectedPhase.fase}: {selectedPhase.nombre}
            </h3>
            <span className="text-xs font-semibold text-brand-700 bg-brand-100 px-2 py-0.5 rounded-full">
              Estado: {selectedPhase.estado}
            </span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            {selectedPhase.descripcion}
          </p>
          <div className="pt-2 text-xs text-slate-700">
            <span className="font-bold text-slate-900">Artefactos y evidencia:</span> {selectedPhase.artefactos}
          </div>
        </div>
      </section>
    </div>
  );
}

