"""
Fase 4.1 — Precio implícito por año
Fuente: data/processed/chaco_serie_mensual_2002_2026.csv

El "precio implícito" es una aproximación al precio efectivo recibido por
tonelada exportada: FOB_dólar / Peso neto. No es el precio internacional
de ningún commodity puntual (eso es la Fase 4.4) — es un promedio que
mezcla todos los rubros de Chaco juntos, así que un cambio en la
COMPOSICIÓN de lo exportado (más o menos algodón, más o menos maíz) puede
mover este número tanto como un cambio real de precios. Ese matiz se
retoma en la Fase 4.6 (composición por Rubro).

Uso desde notebook:
    %run ../src/fase4_precio_implicito.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"

# ─── CARGA ───────────────────────────────────────────────────────────────────
df = pd.read_csv(ARCHIVO)

# ─── AGREGACIÓN ANUAL ─────────────────────────────────────────────────────────
anual = df.groupby("Año")[["FOB_dólar", "Peso neto"]].sum()
anual["precio_implicito_usd_ton"] = (anual["FOB_dólar"] / anual["Peso neto"]) * 1000
# *1000 porque Peso neto está en kg; USD/tonelada = USD/kg * 1000

anual["FOB_millones_usd"] = anual["FOB_dólar"] / 1e6
anual["toneladas"] = anual["Peso neto"] / 1000

# ─── AÑO INCOMPLETO: marcar 2026 explícitamente ──────────────────────────────
meses_2026 = sorted(df[df["Año"] == 2026]["Mes"].unique())
es_parcial = len(meses_2026) < 12

# ─── REPORTE ────────────────────────────────────────────────────────────────
print("=" * 74)
print("FASE 4.1 — PRECIO IMPLÍCITO POR AÑO (USD/tonelada)")
print("Provincia: Chaco")
print("=" * 74)

print(f"\n{'Año':<8}{'FOB (M USD)':>15}{'Toneladas':>15}{'USD/tonelada':>18}")
print("-" * 56)
for año, row in anual.iterrows():
    marca = "  (parcial, 6 meses)" if (año == 2026 and es_parcial) else ""
    print(f"{año:<8}{row['FOB_millones_usd']:>15,.1f}{row['toneladas']:>15,.0f}{row['precio_implicito_usd_ton']:>18,.1f}{marca}")

# ─── VARIACIÓN INTERANUAL DEL PRECIO IMPLÍCITO ───────────────────────────────
anual["var_precio_pct"] = anual["precio_implicito_usd_ton"].pct_change() * 100

print("\n" + "=" * 74)
print("VARIACIÓN INTERANUAL DEL PRECIO IMPLÍCITO")
print("=" * 74)
recientes = anual.loc[anual.index >= 2020]
for año, row in recientes.iterrows():
    var = row["var_precio_pct"]
    var_str = f"{var:+.1f}%" if pd.notna(var) else "—"
    print(f"  {año}  →  USD {row['precio_implicito_usd_ton']:>7,.1f}/ton  ({var_str} vs. año anterior)")

print("\n" + "=" * 74)
print("📌 NOTA")
print("=" * 74)
print("2026 es un año parcial (solo 6 de 12 meses) — el precio implícito")
print("de 2026 NO es directamente comparable al de años completos sin ese")
print("matiz, aunque el promedio en sí no tiene el mismo sesgo que un total")
print("acumulado (no se \"pierde\" magnitud por faltar meses, pero sí puede")
print("estar sesgado si la mezcla de rubros de la primera mitad del año es")
print("distinta a la del año completo).")
print("=" * 74)