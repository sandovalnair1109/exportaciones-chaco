"""
Fase 4.4 — Precio implícito de Chaco vs. precio internacional de la soja
Fuentes:
    - data/processed/chaco_serie_mensual_2002_2026.csv  (precio implícito de Chaco, Fase 4.1)
    - data/raw/prod_soja_acum_2002_2025.xlsx, hoja 'soja_ncm_acum'
      (complejo soja NACIONAL, sin desglose por provincia — ver docs/inventario_datasets.md)

Qué compara:
    El precio implícito de Chaco (Fase 4.1) es un promedio de TODOS los
    rubros de la provincia (PP/MOA/MOI/CyE) — mezcla maíz, algodón,
    quebracho, etc. Este paso lo contrasta contra el precio de un solo
    commodity puntual: porotos de soja crudos (NCM 12010090 / 12019000,
    mismo producto, códigos sucesivos sin superposición — ver celda de
    verificación más abajo), a nivel NACIONAL.

    Sirve para responder: cuando el precio implícito de Chaco sube o baja,
    ¿es porque el precio internacional de referencia (soja) se movió en la
    misma dirección? Si NO se mueven juntos, es una señal más de que la
    composición de lo que exporta Chaco (no el precio internacional) es lo
    que domina — reforzando el hallazgo de la Fase 4.3.

Limitación importante:
    Esto NO es un precio de pizarra internacional (ej. Chicago Board of
    Trade) — es el precio implícito de las exportaciones ARGENTINAS de
    porotos de soja crudos (FOB/kg). Es un proxy razonable (Argentina es
    tomador de precio en soja, no formador), pero no es la fuente primaria
    del precio internacional. Documentar esta limitación en la matriz de
    citas si se usa la cifra en conclusiones.

Uso desde notebook:
    %run ../src/fase4_precio_soja_internacional.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO_CHACO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"
ARCHIVO_SOJA = RAIZ / "data" / "raw" / "exports_2025_Y" / "prod_soja_acum_2002_2025.xlsx"
HOJA_SOJA = "soja_ncm_acum"

# Códigos NCM de "porotos de soja crudos, excluidos para siembra" a través
# del tiempo. Verificado: sin superposición año a año (2002-2011 usa el
# primero, 2012-2025 el segundo), así que se pueden sumar sin doble conteo.
NCM_POROTOS_SOJA = [12010090, 12019000]

# ─── 1. PRECIO IMPLÍCITO DE CHACO (mismo cálculo que Fase 4.1) ─────────────
df_chaco = pd.read_csv(ARCHIVO_CHACO)
anual_chaco = df_chaco.groupby("Año")[["FOB_dólar", "Peso neto"]].sum()
anual_chaco["precio_chaco_usd_ton"] = (anual_chaco["FOB_dólar"] / anual_chaco["Peso neto"]) * 1000

# ─── 2. PRECIO INTERNACIONAL DE LA SOJA (porotos crudos, nacional) ─────────
df_soja = pd.read_excel(ARCHIVO_SOJA, sheet_name=HOJA_SOJA, header=0)

# La columna FOB se llama distinto según el año de descarga del archivo
# (FOB(USD) en versiones viejas, FOB(dol) en esta) — normalizamos.
col_fob = [c for c in df_soja.columns if c.lower().startswith("fob")][0]

porotos = df_soja[df_soja["NCM"].isin(NCM_POROTOS_SOJA)].copy()

# Verificación: un solo código NCM por año, sin superposición (si esto
# fallara, sumar directamente duplicaría o mezclaría series distintas)
codigos_por_año = porotos.groupby("año")["NCM"].nunique()
assert (codigos_por_año == 1).all(), (
    f"Hay años con más de un código NCM para porotos de soja crudos — "
    f"revisar antes de sumar:\n{codigos_por_año[codigos_por_año > 1]}"
)

anual_soja = porotos.groupby("año")[["pnet(kg)", col_fob]].sum()
anual_soja.columns = ["peso_kg", "fob_usd"]
anual_soja["precio_soja_usd_ton"] = (anual_soja["fob_usd"] / anual_soja["peso_kg"]) * 1000

# ─── 3. UNIÓN Y COMPARACIÓN ─────────────────────────────────────────────────
comparacion = anual_chaco[["precio_chaco_usd_ton"]].join(
    anual_soja[["precio_soja_usd_ton"]], how="inner"
)
comparacion["var_chaco_pct"] = comparacion["precio_chaco_usd_ton"].pct_change() * 100
comparacion["var_soja_pct"] = comparacion["precio_soja_usd_ton"].pct_change() * 100

# ¿Se movieron en la misma dirección año a año? (señal simple de correlación direccional)
comparacion["misma_direccion"] = (
    (comparacion["var_chaco_pct"] > 0) == (comparacion["var_soja_pct"] > 0)
)

# ─── REPORTE ─────────────────────────────────────────────────────────────
print("=" * 84)
print("FASE 4.4 — PRECIO IMPLÍCITO DE CHACO vs. PRECIO DE LA SOJA (porotos crudos, nacional)")
print("=" * 84)

ventana = comparacion.loc[2015:2026]
print(f"\n{'Año':<6}{'Chaco (USD/ton)':>18}{'Soja (USD/ton)':>18}{'Δ% Chaco':>12}{'Δ% Soja':>12}{'¿Misma dir.?':>15}")
print("-" * 84)
for año, row in ventana.iterrows():
    var_c = f"{row['var_chaco_pct']:+.1f}%" if pd.notna(row['var_chaco_pct']) else "—"
    var_s = f"{row['var_soja_pct']:+.1f}%" if pd.notna(row['var_soja_pct']) else "—"
    misma = "✅ sí" if row["misma_direccion"] else ("❌ no" if pd.notna(row["var_chaco_pct"]) else "—")
    print(f"{año:<6}{row['precio_chaco_usd_ton']:>18,.1f}{row['precio_soja_usd_ton']:>18,.1f}{var_c:>12}{var_s:>12}{misma:>15}")

# ─── CORRELACIÓN Y COINCIDENCIA DIRECCIONAL ─────────────────────────────────
correlacion = comparacion["precio_chaco_usd_ton"].corr(comparacion["precio_soja_usd_ton"])
años_comparables = comparacion["misma_direccion"].dropna()
pct_misma_direccion = años_comparables.mean() * 100

print("\n" + "=" * 84)
print("📊 RESUMEN")
print("=" * 84)
print(f"Correlación (niveles, toda la serie común): {correlacion:.2f}")
print(f"Años en que ambos precios se movieron en la misma dirección: "
      f"{años_comparables.sum()}/{len(años_comparables)} ({pct_misma_direccion:.0f}%)")

print("\n" + "=" * 84)
print("📌 FOCO 2022-2024 (la caída)")
print("=" * 84)
foco = comparacion.loc[2022:2024]
for año, row in foco.iterrows():
    print(f"  {año}: Chaco {row['precio_chaco_usd_ton']:>7,.1f} USD/ton  |  "
          f"Soja {row['precio_soja_usd_ton']:>7,.1f} USD/ton")

print("\n" + "=" * 84)
print("📌 NOTA")
print("=" * 84)
print("Este precio de soja es un proxy (precio implícito de exportación argentina")
print("de porotos crudos), no una cotización internacional de pizarra. Ver docstring")
print("del script para el detalle de la limitación antes de citar en conclusiones.")
print("=" * 84)