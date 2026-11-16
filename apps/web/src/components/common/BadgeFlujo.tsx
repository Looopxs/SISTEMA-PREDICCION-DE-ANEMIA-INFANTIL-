"use client";

import React from "react";
import { Activity, Sparkles, AlertCircle } from "lucide-react";

interface BadgeFlujoProps {
  tipo: "OBSERVADO" | "PREDICCION_IA" | "A" | "B";
  showDisclaimer?: boolean;
}

export function BadgeFlujo({ tipo, showDisclaimer = false }: BadgeFlujoProps) {
  const isObservado = tipo === "OBSERVADO" || tipo === "A";

  if (isObservado) {
    return (
      <div className="flex flex-col gap-1">
        <div className="inline-flex items-center gap-1.5 self-start rounded-md border border-emerald-300 bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-800 shadow-2xs">
          <Activity className="h-3.5 w-3.5 text-emerald-600" />
          <span>FLUJO A: EVALUACIÓN ANTROPOMÉTRICA / HB OBSERVADA (CLÍNICA — NO IA)</span>
        </div>
        {showDisclaimer && (
          <p className="text-[11px] text-slate-500">
            Cálculo determinístico oficial basado en Patrones OMS 2006 (HAZ/WAZ) y corrección de Hb por altitud OMS 2024.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="inline-flex items-center gap-1.5 self-start rounded-md border border-ai-300 bg-ai-50 px-2.5 py-1 text-xs font-bold text-ai-800 shadow-2xs">
        <Sparkles className="h-3.5 w-3.5 text-ai-600" />
        <span>FLUJO B: PREDICCIÓN PROBABILÍSTICA IA (PREVIA A MEDICIONES — PRE-TEST)</span>
      </div>
      {showDisclaimer && (
        <p className="text-[11px] text-slate-500 flex items-center gap-1">
          <AlertCircle className="h-3 w-3 text-ai-600 shrink-0" />
          <span>Covariables sociodemográficas pre-medición sin filtración de biomarcadores (Zero Data Leakage).</span>
        </p>
      )}
    </div>
  );
}
