"""
Fase 4.6 — Composición por Rubro (PP/MOA/MOI/CyE)
Fuente: data/processed/chaco_serie_mensual_2002_2026.csv

Pregunta: ¿cambió QUÉ exporta Chaco entre el pico (2022) y la
recuperación (2026), o exporta lo mismo en menor cantidad?

Ya sabemos (Fase 4.3) que la caída/recuperación es de volumen, no de
precio. Este paso mira si ese volumen perdido/recuperado se concentra en
algún Rubro en particular (ej. ¿se cayó más el campo — Productos
Primarios — que la industria — MOI?), o si la composición se mantuvo
estable y todos los rubros se movieron más o menos parejo.

Rubros (clasificación INDEC):
    PP  = Productos primarios (materia prima sin procesar: granos, fibras)
    MOA = Manufacturas de origen agropecuario (procesado agroindustrial)
    MOI = Manufacturas de origen industrial
    CyE = Combustibles y energía

⚠️ Nota sobre 2026: año parcial (6 de 12 meses). La composición por
% debería ser razonablemente comparable igual (no depende tanto de la
magnitud absoluta como el volumen o el FOB), pero si algún Rubro tiene
estacionalidad marcada dentro del año, el % de 2026 puede estar sesgado
por cubrir solo el primer semestre. Se deja marcado en la tabla.

Uso desde notebook:
    %run ../src/fase4_composicion_rubro.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"

df = pd.read_csv(ARCHIVO)

# ─── 1. FOB POR AÑO Y RUBRO ──────────────────────────────────────────────────
tabla = df.groupby(["Año", "Rubro"])["FOB_dólar"].sum().unstack("Rubro").fillna(0)

# Nombres cortos para las columnas, más legibles en la tabla
RENOMBRE = {
    "Productos primarios (PP)": "PP",
    "Manufacturas de origen agropecuario (MOA)": "MOA",
    "Manufacturas de origen industrial (MOI)": "MOI",
    "Combustibles y energía (CyE)": "CyE",
}
tabla = tabla.rename(columns=RENOMBRE)
ORDEN_RUBROS = ["PP", "MOA", "MOI", "CyE"]
tabla = tabla[[c for c in ORDEN_RUBROS if c in tabla.columns]]

tabla["TOTAL"] = tabla.sum(axis=1)

# ─── 2. COMPOSICIÓN EN % ─────────────────────────────────────────────────────
composicion_pct = tabla[ORDEN_RUBROS].div(tabla["TOTAL"], axis=0) * 100

meses_2026 = sorted(df[df["Año"] == 2026]["Mes"].unique())
es_parcial_2026 = len(meses_2026) < 12

# ─── REPORTE ─────────────────────────────────────────────────────────────
print("=" * 84)
print("FASE 4.6 — COMPOSICIÓN POR RUBRO (% del total FOB de Chaco, por año)")
print("=" * 84)

ventana = composicion_pct.loc[2015:2026]
print(f"\n{'Año':<6}" + "".join(f"{r:>10}" for r in ORDEN_RUBROS))
print("-" * (6 + 10 * len(ORDEN_RUBROS)))
for año, row in ventana.iterrows():
    marca = "  (parcial)" if (año == 2026 and es_parcial_2026) else ""
    print(f"{año:<6}" + "".join(f"{row[r]:>9.1f}%" for r in ORDEN_RUBROS) + marca)

# ─── 3. FOCO: 2022 vs 2024 vs 2026 (comparación directa) ────────────────────
print("\n" + "=" * 84)
print("📊 COMPARACIÓN DIRECTA — 2022 (pico) vs. 2024 (piso) vs. 2026 (recuperación)")
print("=" * 84)
años_foco = [a for a in [2022, 2024, 2026] if a in composicion_pct.index]
comp_foco = composicion_pct.loc[años_foco, ORDEN_RUBROS]

print(f"\n{'Rubro':<8}" + "".join(f"{a:>12}" for a in años_foco) + f"{'Δ pp (22→26)':>16}")
print("-" * (8 + 12 * len(años_foco) + 16))
for rubro in ORDEN_RUBROS:
    valores = comp_foco[rubro]
    delta = valores.iloc[-1] - valores.iloc[0] if len(valores) > 1 else float("nan")
    fila = "".join(f"{v:>11.1f}%" for v in valores)
    print(f"{rubro:<8}{fila}{delta:>+15.1f}pp")

# ─── 4. VOLUMEN FOB ABSOLUTO POR RUBRO, PARA COMPLEMENTAR EL % ─────────────
# ⚠️ 2024 es año completo, 2026 es parcial (solo H1) — comparar el FOB
# absoluto de 2022 (año completo) contra 2026 (6 meses) exageraría la caída
# de cualquier rubro solo por el recorte de calendario, no por actividad real.
# Mismo criterio que Fase 1.11 y Fase 4.3: para 2026 se usa el primer
# semestre de CADA año en la comparación, no el año completo.
print("\n" + "=" * 84)
print("📊 FOB ABSOLUTO POR RUBRO (millones USD) — Primer semestre: 2022 vs 2024 vs 2026")
print("=" * 84)
tabla_h1 = (
    df[df["Mes"] <= 6]
    .groupby(["Año", "Rubro"])["FOB_dólar"].sum()
    .unstack("Rubro").fillna(0).rename(columns=RENOMBRE)
)
tabla_h1 = tabla_h1[[c for c in ORDEN_RUBROS if c in tabla_h1.columns]]
fob_foco = tabla_h1.loc[años_foco, ORDEN_RUBROS] / 1e6
print(f"\n{'Rubro':<8}" + "".join(f"{a:>14}" for a in años_foco) + f"{'Δ% (22→26)':>14}")
print("-" * (8 + 14 * len(años_foco) + 14))
for rubro in ORDEN_RUBROS:
    valores = fob_foco[rubro]
    delta_pct = (valores.iloc[-1] / valores.iloc[0] - 1) * 100 if valores.iloc[0] != 0 and len(valores) > 1 else float("nan")
    fila = "".join(f"{v:>13,.1f}" for v in valores)
    print(f"{rubro:<8}{fila}{delta_pct:>+13.1f}%")

# ─── 5. RUBRO QUE MÁS PESO GANÓ/PERDIÓ ──────────────────────────────────────
if 2022 in composicion_pct.index and 2026 in composicion_pct.index:
    cambios = (composicion_pct.loc[2026, ORDEN_RUBROS] - composicion_pct.loc[2022, ORDEN_RUBROS]).sort_values()
    print("\n" + "=" * 84)
    print("📌 RANKING DE CAMBIO DE PESO RELATIVO (2022 → 2026, en puntos porcentuales)")
    print("=" * 84)
    for rubro, delta in cambios.items():
        signo = "ganó" if delta > 0 else "perdió"
        print(f"  {rubro:<6} {signo} {abs(delta):.1f} puntos porcentuales")

print("\n" + "=" * 84)
print("📌 NOTA")
print("=" * 84)
print("2026 es parcial (solo primer semestre) — si algún rubro tiene estacionalidad")
print("marcada dentro del año (ej. cosecha concentrada en ciertos meses), su % en")
print("2026 puede no ser representativo del año completo. Confirmar con Fase 2")
print("(estacionalidad) antes de sacar conclusiones fuertes sobre el rubro más chico.")
print("=" * 84)