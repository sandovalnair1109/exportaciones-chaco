"""
Fase 4.2 — Gráfico del precio implícito por año
Fuente: data/processed/chaco_serie_mensual_2002_2026.csv

Grafica la serie de precio implícito (USD/tonelada) calculada en la Fase 4.1,
recortada a la ventana 2015-2026 (la misma que usa la tabla resumen de la
Fase 1.9, para mantener consistencia entre gráficos del proyecto).

2026 se marca visualmente distinto (año parcial, 6 de 12 meses) para no
sugerir que es comparable 1 a 1 con años completos.

Uso desde notebook:
    %run ../src/fase4_grafico_precio_implicito.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"

# ─── CARGA Y CÁLCULO (mismo criterio que fase4_precio_implicito.py) ─────────
df = pd.read_csv(ARCHIVO)

anual = df.groupby("Año")[["FOB_dólar", "Peso neto"]].sum()
anual["precio_implicito_usd_ton"] = (anual["FOB_dólar"] / anual["Peso neto"]) * 1000

# Recorte a la ventana de la Fase 1.9, para consistencia visual con esos gráficos
serie = anual.loc[2015:2026, "precio_implicito_usd_ton"]

meses_2026 = sorted(df[df["Año"] == 2026]["Mes"].unique())
es_parcial = len(meses_2026) < 12

# ─── GRÁFICO ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5))

# Separamos 2015-2025 (completos) de 2026 (parcial) para distinguirlos visualmente
completos = serie.loc[:2025]
ax.plot(completos.index, completos.values, marker="o", color="tab:blue", label="Años completos")

if es_parcial and 2026 in serie.index:
    # Línea punteada conectando 2025→2026, y marcador distinto para 2026
    ax.plot([2025, 2026], [serie.loc[2025], serie.loc[2026]],
            linestyle="--", color="tab:blue", alpha=0.6)
    ax.plot(2026, serie.loc[2026], marker="D", color="tab:red",
             markersize=9, label="2026 (parcial, 6 meses)")

for año in [2022, 2024]:
    if año in serie.index:
        ax.axvline(año, color="gray", linestyle=":", alpha=0.5)

ax.set_title("Precio implícito de las exportaciones de Chaco (USD/tonelada) — 2015-2026")
ax.set_xlabel("Año")
ax.set_ylabel("USD / tonelada")
ax.set_xticks(serie.index)
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.show()