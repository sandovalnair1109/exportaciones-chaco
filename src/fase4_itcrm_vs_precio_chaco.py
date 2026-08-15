"""
Fase 4.5 — Efecto del tipo de cambio real (ITCRM) sobre el precio implícito de Chaco
Fuentes:
    - data/processed/chaco_serie_mensual_2002_2026.csv  (precio implícito de Chaco, Fase 4.1)
    - data/raw/ITCRM_serie_historica.xlsx, hoja 'ITCRM y bilaterales prom. mens.'
      (BCRA, índice de tipo de cambio real multilateral, base 17-12-15=100)

Pregunta que responde (distinta a la Fase 4.4):
    La Fase 4.4 comparó a Chaco contra el precio internacional de un commodity
    puntual (soja). Esto es otra cosa: si el peso se apreció en TÉRMINOS REALES
    entre 2022 y 2024 (ITCRM más bajo = peso más apreciado, exportaciones menos
    competitivas), eso podría explicar parte de la caída del precio implícito
    en USD, más allá de si el precio internacional de cada producto subió o bajó.

Nota sobre la hoja usada:
    docs/inventario_datasets.md anotaba que había que promediar la serie DIARIA
    a mensual con resample('MS').mean(). Resulta innecesario: el archivo ya trae
    una hoja de promedios mensuales pre-calculada ('ITCRM y bilaterales prom.
    mens.'), que es la que se usa acá. Se deja esta nota para no repetir el
    trabajo si alguien retoma el archivo más adelante.

    La hoja mensual trae 3 filas de pie (NaN, "Nota: Datos provisorios...",
    "Fuente: INDEC...") que hay que descartar antes de operar con fechas.

Comparación año a año:
    Para que sea comparable, el promedio anual de ITCRM se calcula SOLO sobre
    los meses que también están presentes en la serie de Chaco ese año (ej.
    2026: Chaco solo tiene Ene-Jun, así que el ITCRM de 2026 acá es el
    promedio Ene-Jun, no el promedio de los 7 meses disponibles en el archivo
    del BCRA).

Uso desde notebook:
    %run ../src/fase4_itcrm_vs_precio_chaco.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO_CHACO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"
ARCHIVO_ITCRM = RAIZ / "data" / "raw" / "ITCRM_serie_historica.xlsx"
HOJA_ITCRM = "ITCRM y bilaterales prom. mens."

# ─── 1. PRECIO IMPLÍCITO DE CHACO, ANUAL Y MENSUAL (mismo criterio de Fase 4.1) ──
df_chaco = pd.read_csv(ARCHIVO_CHACO)

anual_chaco = df_chaco.groupby("Año")[["FOB_dólar", "Peso neto"]].sum()
anual_chaco["precio_chaco_usd_ton"] = (anual_chaco["FOB_dólar"] / anual_chaco["Peso neto"]) * 1000

# Meses realmente presentes por año en la serie de Chaco (para recortar el ITCRM igual)
meses_presentes_por_año = df_chaco.groupby("Año")["Mes"].unique().apply(set)

# ─── 2. ITCRM MENSUAL (limpieza de filas de pie de página) ─────────────────
df_itcrm = pd.read_excel(ARCHIVO_ITCRM, sheet_name=HOJA_ITCRM, header=1)
df_itcrm = df_itcrm.rename(columns={"ITCRM ": "itcrm"})  # ojo: espacio al final en el original
df_itcrm["Período"] = pd.to_datetime(df_itcrm["Período"], errors="coerce")
df_itcrm = df_itcrm.dropna(subset=["Período", "itcrm"]).copy()

df_itcrm["Año"] = df_itcrm["Período"].dt.year
df_itcrm["Mes"] = df_itcrm["Período"].dt.month

# ─── 3. PROMEDIO ANUAL DE ITCRM, RECORTADO A LOS MESES QUE TIENE CHACO ─────
def itcrm_anual_comparable(año: int) -> float | None:
    meses_chaco = meses_presentes_por_año.get(año)
    if meses_chaco is None:
        return None
    filtro = (df_itcrm["Año"] == año) & (df_itcrm["Mes"].isin(meses_chaco))
    valores = df_itcrm.loc[filtro, "itcrm"]
    return valores.mean() if not valores.empty else None

itcrm_por_año = {año: itcrm_anual_comparable(año) for año in anual_chaco.index}
anual_chaco["itcrm_prom"] = pd.Series(itcrm_por_año)

# ─── 4. COMPARACIÓN ─────────────────────────────────────────────────────────
comparacion = anual_chaco.dropna(subset=["itcrm_prom"]).copy()
comparacion["var_precio_pct"] = comparacion["precio_chaco_usd_ton"].pct_change() * 100
comparacion["var_itcrm_pct"] = comparacion["itcrm_prom"].pct_change() * 100
comparacion["misma_direccion"] = (
    (comparacion["var_precio_pct"] > 0) == (comparacion["var_itcrm_pct"] > 0)
)

# ─── REPORTE ─────────────────────────────────────────────────────────────
print("=" * 90)
print("FASE 4.5 — ITCRM vs. PRECIO IMPLÍCITO DE CHACO")
print("=" * 90)

ventana = comparacion.loc[2015:2026]
print(f"\n{'Año':<6}{'Precio Chaco (USD/ton)':>24}{'ITCRM (prom.)':>16}{'Δ% Precio':>12}{'Δ% ITCRM':>12}{'¿Misma dir.?':>15}")
print("-" * 90)
for año, row in ventana.iterrows():
    vp = f"{row['var_precio_pct']:+.1f}%" if pd.notna(row['var_precio_pct']) else "—"
    vi = f"{row['var_itcrm_pct']:+.1f}%" if pd.notna(row['var_itcrm_pct']) else "—"
    misma = "✅ sí" if row["misma_direccion"] else ("❌ no" if pd.notna(row["var_precio_pct"]) else "—")
    marca = "  (parcial, Ene-Jun)" if año == 2026 else ""
    print(f"{año:<6}{row['precio_chaco_usd_ton']:>24,.1f}{row['itcrm_prom']:>16,.1f}{vp:>12}{vi:>12}{misma:>15}{marca}")

correlacion = comparacion["precio_chaco_usd_ton"].corr(comparacion["itcrm_prom"])
años_comparables = comparacion["misma_direccion"].dropna()
pct_misma_direccion = años_comparables.mean() * 100

print("\n" + "=" * 90)
print("📊 RESUMEN")
print("=" * 90)
print(f"Correlación (niveles, toda la serie común): {correlacion:.2f}")
print(f"Años en que precio Chaco e ITCRM se movieron en la misma dirección: "
      f"{años_comparables.sum()}/{len(años_comparables)} ({pct_misma_direccion:.0f}%)")

print("\n" + "=" * 90)
print("📌 FOCO 2022-2024 (¿la apreciación real explica la caída?)")
print("=" * 90)
foco = comparacion.loc[2022:2024]
for año, row in foco.iterrows():
    print(f"  {año}: Precio Chaco {row['precio_chaco_usd_ton']:>7,.1f} USD/ton  |  "
          f"ITCRM {row['itcrm_prom']:>6,.1f}  (índice más bajo = peso más apreciado en términos reales)")

var_itcrm_22_24 = (comparacion.loc[2024, "itcrm_prom"] / comparacion.loc[2022, "itcrm_prom"] - 1) * 100
var_precio_22_24 = (comparacion.loc[2024, "precio_chaco_usd_ton"] / comparacion.loc[2022, "precio_chaco_usd_ton"] - 1) * 100
print(f"\n  Variación ITCRM 2022→2024:         {var_itcrm_22_24:+.1f}%")
print(f"  Variación precio implícito 2022→2024: {var_precio_22_24:+.1f}%")

print("\n" + "=" * 90)
print("📌 NOTA")
print("=" * 90)
print("El ITCRM mide competitividad cambiaria (peso vs. socios comerciales), no")
print("determina mecánicamente el precio FOB en USD que paga el comprador externo.")
print("Una correlación aquí es una señal a investigar, no una prueba causal — mismo")
print("criterio de correlación/causalidad ya usado en la Fase 3 del proyecto.")
print("=" * 90)