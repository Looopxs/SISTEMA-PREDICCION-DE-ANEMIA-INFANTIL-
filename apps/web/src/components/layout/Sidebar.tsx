"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Database,
  ShieldAlert,
  Activity,
  BrainCircuit,
  Cpu,
  Sparkles,
  Network,
  Globe2,
  BarChart3,
  FileText,
  History,
  Settings,
  ChevronLeft,
  ChevronRight,
  HeartPulse,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard Epidemiológico", icon: LayoutDashboard },
  { href: "/datasets", label: "Gestión de Datasets", icon: Database },
  { href: "/calidad-datos", label: "Control de Calidad", icon: ShieldAlert },
  { href: "/antropometria", label: "Antropometría y Hb (Obs.)", icon: Activity },
  { href: "/experimentos", label: "Laboratorio M1–M5", icon: BrainCircuit },
  { href: "/modelos", label: "Modelos y Model Cards", icon: Cpu },
  { href: "/predicciones", label: "Inferencia de Riesgo (IA)", icon: Sparkles },
  { href: "/explicabilidad", label: "Explicabilidad SHAP", icon: Network },
  { href: "/geografia", label: "Geografía y Equidad", icon: Globe2 },
  { href: "/estadistica", label: "Laboratorio Estadístico", icon: BarChart3 },
  { href: "/reportes", label: "Reportes PDF / Excel", icon: FileText },
  { href: "/auditoria", label: "Bitácora de Auditoría", icon: History },
  { href: "/configuracion", label: "Configuración", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`relative flex flex-col border-r border-slate-200 bg-white transition-all duration-300 z-30 ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between border-b border-slate-100 px-4">
        <Link href="/" className="flex items-center gap-3 overflow-hidden">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-ai-600 text-white shadow-md">
            <HeartPulse className="h-5 w-5" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="text-base font-bold tracking-tight text-slate-900">
                NutriPredict <span className="text-ai-600 font-extrabold">AI</span>
              </span>
              <span className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">
                Vigilancia Nutricional
              </span>
            </div>
          )}
        </Link>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          title={collapsed ? "Expandir menú" : "Colapsar menú"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                isActive
                  ? "bg-brand-50 text-brand-700 font-semibold shadow-xs"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              }`}
              title={collapsed ? item.label : undefined}
            >
              <Icon
                className={`h-5 w-5 shrink-0 ${
                  isActive ? "text-brand-600" : "text-slate-400 group-hover:text-slate-600"
                }`}
              />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </div>

      {/* CRISP-DM Badge */}
      {!collapsed && (
        <div className="p-4 border-t border-slate-100 bg-slate-50/50">
          <div className="rounded-xl border border-slate-200/80 bg-white p-3 shadow-xs">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1">
              <span>Metodología CRISP-DM</span>
              <span className="text-[10px] text-brand-600 bg-brand-50 px-1.5 py-0.5 rounded font-mono">Fases 1-6</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-tight">
              Flujo trazable: Comprensión &rarr; Preparación &rarr; Modelado &rarr; Evaluación &rarr; Despliegue.
            </p>
          </div>
        </div>
      )}

      {/* User Footer */}
      <div className="border-t border-slate-100 p-3 flex items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-200 text-xs font-bold text-slate-700">
          CR
        </div>
        {!collapsed && (
          <div className="flex flex-col overflow-hidden">
            <span className="truncate text-xs font-semibold text-slate-800">
              Dr. Carlos Ramos
            </span>
            <span className="truncate text-[10px] text-slate-400">
              Investigador Principal
            </span>
          </div>
        )}
      </div>
    </aside>
  );
}

