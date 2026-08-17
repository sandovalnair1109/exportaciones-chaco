"""
Fase 4.8.c — Gráfico simple: serie mensual de Chaco (PP) con las ventanas
de retenciones marcadas
Fuentes:
    - data/processed/chaco_serie_mensual_2002_2026.csv
    - data/raw/retenciones_chaco.csv

Por qué un gráfico "simple" y no un cruce exhaustivo:
    La Fase 4.8.b (dos chequeos: total de Chaco y solo PP) encontró señal
    débil — los meses con cambio de decreto no se distinguen claramente de
    los meses sin cambio, a nivel mensual agregado. Este gráfico deja
    constancia visual de esa comparación, no busca demostrar un efecto que
    los números ya mostraron que no aparece con claridad en este recorte.

Uso desde notebook:
    %run ../src/fase4_grafico_retenciones_vs_serie.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO_CHACO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"
ARCHIVO_RETENCIONES = RAIZ / "data" / "raw" / "retenciones_chaco.csv"

RUBRO_PP = "Productos primarios (PP)"

# ─── 1. SERIE MENSUAL DE PP, 2024-2026 (para dar contexto previo al 2025) ──
df = pd.read_csv(ARCHIVO_CHACO)
df_pp = df[df["Rubro"] == RUBRO_PP].copy()
df_pp["fecha"] = pd.to_datetime(df_pp["Año"].astype(str) + "-" + df_pp["Mes"].astype(str) + "-01")

mensual = df_pp.groupby("fecha")["FOB_dólar"].sum().sort_index()
mensual = mensual.loc["2024-01-01":]

# ─── 2. FECHAS DE ENTRADA EN VIGENCIA DE CADA DECRETO ──────────────────────
retenciones = pd.read_csv(ARCHIVO_RETENCIONES, sep=";")
retenciones["fecha_inicio_dt"] = pd.to_datetime(retenciones["fecha_inicio"])
decretos_fecha = retenciones.groupby("decreto")["fecha_inicio_dt"].min().sort_values()

# ─── GRÁFICO ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5.5))

ax.plot(mensual.index, mensual.values / 1e6, marker="o", color="tab:green", linewidth=1.8)

colores = plt.cm.tab10.colors
for i, (decreto, fecha) in enumerate(decretos_fecha.items()):
    color = colores[i % len(colores)]
    ax.axvline(fecha, color=color, linestyle="--", alpha=0.6)
    ax.annotate(
        decreto,
        xy=(fecha, ax.get_ylim()[1]),
        xytext=(2, -10 - (i % 3) * 12),
        textcoords="offset points",
        rotation=90,
        va="top",
        ha="left",
        fontsize=8,
        color=color,
    )

ax.set_title("Chaco — Exportaciones mensuales de Productos Primarios (FOB, M USD)\ncon fecha de entrada en vigencia de cada decreto de retenciones")
ax.set_xlabel("Mes")
ax.set_ylabel("FOB PP (millones USD)")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()

print("Serie mensual de PP (M USD) — meses con cambio de decreto marcados con 🔶:\n")
meses_con_cambio = {(f.year, f.month) for f in pd.to_datetime(decretos_fecha.values)}
for fecha, valor in mensual.items():
    marca = " 🔶" if (fecha.year, fecha.month) in meses_con_cambio else ""
    print(f"  {fecha.strftime('%Y-%m')}   {valor/1e6:>8,.1f} M USD{marca}")