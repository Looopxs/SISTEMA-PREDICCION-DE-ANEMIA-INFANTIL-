"use client";

import React, { useState, useEffect } from "react";
import { getAuditoria } from "@/lib/api";
import {
  ShieldCheck,
  Calendar,
  User,
  Activity,
  Lock,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Info,
} from "lucide-react";

export default function AuditoriaPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterAction, setFilterAction] = useState<string>("TODAS");

  useEffect(() => {
    getAuditoria()
      .then((data) => setLogs(data))
      .catch((err) => console.error("Error al cargar logs de auditoría:", err))
      .finally(() => setLoading(false));
  }, []);

  const filteredLogs = logs.filter(
    (l) => filterAction === "TODAS" || l.accion.toLowerCase().includes(filterAction.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            Registro de Auditoría y Trazabilidad Bioética
          </h1>
          <p className="text-sm text-muted-foreground">
            Bitácora inmutable de accesos, operaciones sobre datasets, entrenamiento de modelos y descargas de reportes.
          </p>
        </div>
      </div>

      {/* Declaración de Privacidad y No Identificadores */}
      <div className="p-4 bg-secondary/30 border border-border rounded-xl flex items-start gap-3">
        <ShieldCheck className="h-5 w-5 text-primary shrink-0 mt-0.5" />
        <div className="text-xs text-muted-foreground space-y-1">
          <p className="font-bold text-foreground">
            Cumplimiento Estricto de Protección de Datos Personales (Ley N° 29733 de Perú):
          </p>
          <p>
            NutriPredict AI no almacena ni procesa nombres, documentos nacionales de identidad (DNI), direcciones residenciales exactas ni coordenadas de viviendas de niños ni madres. Todas las observaciones utilizan identificadores alfanuméricos desvinculados irreversibles generados en la fase de ingestión.
          </p>
        </div>
      </div>

      {/* Controles de Filtro */}
      <div className="flex items-center gap-3 bg-card border border-border p-3.5 rounded-xl">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <span className="text-xs font-semibold text-muted-foreground">Filtrar por Acción:</span>
        <select
          value={filterAction}
          onChange={(e) => setFilterAction(e.target.value)}
          className="text-xs bg-background border border-border rounded-md px-2.5 py-1.5 font-medium text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="TODAS">Todas las Operaciones</option>
          <option value="LOGIN">Autenticación / Login</option>
          <option value="EXPERIMENTO">Entrenamiento de Modelos</option>
          <option value="REPORTE">Generación de Reportes</option>
          <option value="PREDICCION">Inferencia Multisalida</option>
          <option value="DATASET">Gestión de Datasets</option>
        </select>
        <span className="text-xs text-muted-foreground ml-auto font-mono">
          {filteredLogs.length} eventos registrados
        </span>
      </div>

      {/* Tabla de Eventos de Auditoría */}
      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Lock className="h-4 w-4 text-primary" />
            Eventos del Sistema
          </h2>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-muted-foreground flex items-center justify-center gap-2">
            <Activity className="h-4 w-4 animate-spin text-primary" />
            Cargando registros de auditoría...
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="p-12 text-center text-xs text-muted-foreground">
            No se registran eventos que coincidan con el filtro seleccionado.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-border bg-muted/40 text-muted-foreground font-semibold">
                  <th className="p-3">Marca Temporal</th>
                  <th className="p-3">Actor / Usuario</th>
                  <th className="p-3">Acción Realizada</th>
                  <th className="p-3">Entidad / Recurso</th>
                  <th className="p-3 text-center">Estado</th>
                  <th className="p-3">Detalle / Metadata</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border font-mono text-[11px]">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-muted/20 transition-colors">
                    <td className="p-3 text-muted-foreground whitespace-nowrap">
                      {new Date(log.creado_en).toLocaleString("es-PE")}
                    </td>
                    <td className="p-3 font-semibold text-foreground">
                      {log.usuario_id || "sistema@nutripredict.pe"}
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-secondary text-secondary-foreground text-[10px] font-bold">
                        {log.accion}
                      </span>
                    </td>
                    <td className="p-3 text-muted-foreground">
                      {log.entidad || "general"}
                    </td>
                    <td className="p-3 text-center">
                      <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300 text-[10px] font-bold">
                        ÉXITO
                      </span>
                    </td>
                    <td className="p-3 text-muted-foreground max-w-xs truncate">
                      {typeof log.detalles === "object"
                        ? JSON.stringify(log.detalles)
                        : log.detalles || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

