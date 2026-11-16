"use client";

import React from "react";
import { AlertTriangle, ShieldCheck, Database, FileSpreadsheet, ExternalLink } from "lucide-react";

interface HeaderProps {
  title?: string;
  subtitle?: string;
  isSynthetic?: boolean;
}

export function Header({
  title = "NutriPredict AI",
  subtitle = "Plataforma de Investigación y Vigilancia Nutricional Infantil",
  isSynthetic = true,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/95 px-6 backdrop-blur-md">
      {/* Title / Breadcrumb */}
      <div className="flex flex-col">
        <h1 className="text-lg font-bold text-slate-900 leading-tight flex items-center gap-2">
          {title}
        </h1>
        <p className="text-xs text-slate-500">{subtitle}</p>
      </div>

      {/* Center / Right Badges */}
      <div className="flex items-center gap-3">
        {/* Permanent Synthetic Data Tag (Rule 9) */}
        {isSynthetic ? (
          <div className="flex items-center gap-2 rounded-full border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800 shadow-xs animate-pulse">
            <AlertTriangle className="h-3.5 w-3.5 text-amber-600 shrink-0" />
            <span>DATOS SINTÉTICOS — NO REPRESENTAN LA REALIDAD</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 rounded-full border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800 shadow-xs">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
            <span>MICRODATOS VERIFICADOS (ENDES/DHS)</span>
          </div>
        )}

        {/* Dataset Pill */}
        <div className="hidden md:flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs text-slate-600 font-medium">
          <Database className="h-3.5 w-3.5 text-brand-600" />
          <span>ENDES Perú 2024</span>
        </div>

        {/* Direct Link to Documentation */}
        <a
          href="/reportes"
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-brand-700 transition"
        >
          <FileSpreadsheet className="h-3.5 w-3.5" />
          <span>Exportar Informe</span>
        </a>
      </div>
    </header>
  );
}

