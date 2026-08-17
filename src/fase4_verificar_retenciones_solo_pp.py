"""
Fase 4.8.b (chequeo intermedio) — Repetir la verificación de señal, pero
filtrando SOLO Productos Primarios (PP)
Fuentes:
    - data/processed/chaco_serie_mensual_2002_2026.csv
    - data/raw/retenciones_chaco.csv

Por qué este recorte:
    El chequeo original (fase4_verificar_retenciones_vs_serie.py) usó el
    TOTAL de Chaco (PP+MOA+MOI+CyE) y no encontró señal clara. Pero las
    retenciones de este proyecto son sobre GRANOS (soja/trigo/maíz-sorgo)
    — productos que caen dentro de PP, no de MOA/MOI/CyE. Si el efecto
    existe, puede estar diluido por el resto de la canasta (y ya sabemos,
    Fase 4.6, que MOA le ganó peso a PP en este mismo período).

⚠️ Limitación honesta: la serie de Chaco NO tiene detalle por producto
específico (no se puede aislar "solo soja" o "solo trigo"), solo por
Rubro (PP/MOA/MOI/CyE). El único archivo con ese detalle es el de
microdatos 2024, descartado como fuente confiable (Fase 0, discrepancia
del 86% vs. el oficial). Este chequeo es lo más fino que se puede hacer
con la fuente validada — sigue siendo un proxy, no un aislamiento exacto
de soja/trigo/maíz.

Uso desde notebook:
    %run ../src/fase4_verificar_retenciones_solo_pp.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO_CHACO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"
ARCHIVO_RETENCIONES = RAIZ / "data" / "raw" / "retenciones_chaco.csv"

RUBRO_PP = "Productos primarios (PP)"

# ─── 1. SERIE MENSUAL, SOLO PP ──────────────────────────────────────────────
df = pd.read_csv(ARCHIVO_CHACO)
df_pp = df[df["Rubro"] == RUBRO_PP]

mensual = df_pp.groupby(["Año", "Mes"])[["FOB_dólar", "Peso neto"]].sum().reset_index()
mensual = mensual.sort_values(["Año", "Mes"]).reset_index(drop=True)

def var_interanual(row, columna):
    anterior = mensual[(mensual["Año"] == row["Año"] - 1) & (mensual["Mes"] == row["Mes"])]
    if anterior.empty:
        return None
    valor_anterior = anterior[columna].values[0]
    return (row[columna] - valor_anterior) / valor_anterior * 100

mensual["var_fob_interanual_pct"] = mensual.apply(lambda r: var_interanual(r, "FOB_dólar"), axis=1)
mensual["var_ton_interanual_pct"] = mensual.apply(lambda r: var_interanual(r, "Peso neto"), axis=1)

# ─── 2. MESES CON CAMBIO DE RETENCIÓN ───────────────────────────────────────
retenciones = pd.read_csv(ARCHIVO_RETENCIONES, sep=";")
retenciones["fecha_inicio_dt"] = pd.to_datetime(retenciones["fecha_inicio"])
meses_con_cambio = sorted({(f.year, f.month) for f in retenciones["fecha_inicio_dt"]})

print("=" * 90)
print("FASE 4.8.b (chequeo intermedio) — SOLO PRODUCTOS PRIMARIOS (PP)")
print("=" * 90)

ventana = mensual[mensual["Año"] >= 2025].copy()
ventana["hay_cambio_retencion"] = ventana.apply(
    lambda r: (int(r["Año"]), int(r["Mes"])) in meses_con_cambio, axis=1
)

print(f"\n{'Año-Mes':<10}{'FOB PP (M USD)':>16}{'Δ% interanual':>16}{'Ton. PP':>14}{'Δ% interanual':>16}{'¿Cambio?':>12}")
print("-" * 90)
for _, row in ventana.iterrows():
    fob_m = row["FOB_dólar"] / 1e6
    ton = row["Peso neto"] / 1000
    var_fob = f"{row['var_fob_interanual_pct']:+.1f}%" if pd.notna(row["var_fob_interanual_pct"]) else "—"
    var_ton = f"{row['var_ton_interanual_pct']:+.1f}%" if pd.notna(row["var_ton_interanual_pct"]) else "—"
    marca = "🔶 SÍ" if row["hay_cambio_retencion"] else ""
    print(f"{int(row['Año'])}-{int(row['Mes']):02d}   {fob_m:>16,.1f}{var_fob:>16}{ton:>14,.0f}{var_ton:>16}{marca:>12}")

con_cambio = ventana[ventana["hay_cambio_retencion"]]["var_fob_interanual_pct"].dropna()
sin_cambio = ventana[~ventana["hay_cambio_retencion"]]["var_fob_interanual_pct"].dropna()

print("\n" + "=" * 90)
print("📊 COMPARACIÓN (solo PP)")
print("=" * 90)
print(f"Meses CON cambio — variación interanual promedio:  {con_cambio.mean():+.1f}%  (n={len(con_cambio)})")
print(f"Meses SIN cambio — variación interanual promedio:  {sin_cambio.mean():+.1f}%  (n={len(sin_cambio)})")
print(f"Diferencia: {abs(con_cambio.mean() - sin_cambio.mean()):.1f} puntos porcentuales")

print("\n" + "=" * 90)
print("📌 NOTA")
print("=" * 90)
print("PP mezcla granos (afectados por retenciones) con otros productos primarios")
print("no afectados (ej. quebracho, fibra de algodón sin procesar). Sigue siendo")
print("un proxy, no un aislamiento exacto — pero más ajustado que el total de Chaco.")
print("=" * 90)