"""
Fase 4.9 — Síntesis: ¿qué combinación de factores explica mejor la caída
2022-2024 y la recuperación 2026?
Fuente: data/processed/chaco_serie_mensual_2002_2026.csv

Qué hace este paso (distinto a los anteriores):
    Las Fases 4.1-4.8 evaluaron cada sospechoso por separado (precio propio,
    precio de la soja, ITCRM, composición por Rubro, retenciones). Este paso
    no agrega un sospechoso nuevo — cruza dos de los hallazgos más fuertes
    entre sí: la descomposición precio/volumen (Fase 4.3) y el cambio de
    composición por Rubro (Fase 4.6), para responder una pregunta más fina:
    dentro del "volumen" que domina la Fase 4.3, ¿la caída se concentra en
    Productos Primarios (PP), o está repartida parejo entre PP y MOA?

Uso desde notebook:
    %run ../src/fase4_sintesis_causas.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"

df = pd.read_csv(ARCHIVO)

RENOMBRE = {
    "Productos primarios (PP)": "PP",
    "Manufacturas de origen agropecuario (MOA)": "MOA",
}

# ─── 1. DESCOMPOSICIÓN PRECIO/VOLUMEN, POR RUBRO (PP y MOA por separado) ───
def descomponer_por_rubro(rubro_col: str, año0: int, año1: int, tabla: pd.DataFrame) -> dict:
    p0, p1 = tabla.loc[año0, "precio_usd_ton"], tabla.loc[año1, "precio_usd_ton"]
    q0, q1 = tabla.loc[año0, "toneladas"], tabla.loc[año1, "toneladas"]
    v0, v1 = tabla.loc[año0, "FOB_dólar"], tabla.loc[año1, "FOB_dólar"]
    delta_total = v1 - v0
    efecto_precio = (p1 - p0) * q0
    efecto_volumen = (q1 - q0) * p0
    efecto_interaccion = (p1 - p0) * (q1 - q0)
    return {
        "rubro": rubro_col, "periodo": f"{año0}→{año1}",
        "v0_M": v0 / 1e6, "v1_M": v1 / 1e6, "delta_M": delta_total / 1e6,
        "delta_pct": delta_total / v0 * 100 if v0 else float("nan"),
        "efecto_volumen_M": efecto_volumen / 1e6,
        "efecto_volumen_pct": efecto_volumen / delta_total * 100 if delta_total else float("nan"),
    }

resultados = []
for rubro_nombre, rubro_col in RENOMBRE.items():
    df_r = df[df["Rubro"] == rubro_nombre]
    anual_r = df_r.groupby("Año")[["FOB_dólar", "Peso neto"]].sum()
    anual_r["toneladas"] = anual_r["Peso neto"] / 1000
    anual_r["precio_usd_ton"] = anual_r["FOB_dólar"] / anual_r["toneladas"]

    r1 = descomponer_por_rubro(rubro_col, 2022, 2024, anual_r)
    resultados.append(r1)

    # H1 vs H1 para la recuperación, mismo criterio que Fase 4.3
    h1_r = df_r[df_r["Mes"] <= 6].groupby("Año")[["FOB_dólar", "Peso neto"]].sum()
    h1_r["toneladas"] = h1_r["Peso neto"] / 1000
    h1_r["precio_usd_ton"] = h1_r["FOB_dólar"] / h1_r["toneladas"]
    r2 = descomponer_por_rubro(rubro_col, 2022, 2026, h1_r)
    r2["periodo"] = "2022→2026 (H1 vs H1)"
    resultados.append(r2)

print("=" * 92)
print("FASE 4.9 — SÍNTESIS: PRECIO/VOLUMEN CRUZADO CON COMPOSICIÓN POR RUBRO")
print("=" * 92)

print(f"\n{'Rubro':<8}{'Período':<24}{'Valor 0 (M)':>13}{'Valor 1 (M)':>13}{'Δ Total (M)':>13}{'Δ%':>10}{'Ef. volumen (M)':>17}{'% del Δ':>10}")
print("-" * 108)
for r in resultados:
    print(f"{r['rubro']:<8}{r['periodo']:<24}{r['v0_M']:>13,.1f}{r['v1_M']:>13,.1f}{r['delta_M']:>+13,.1f}{r['delta_pct']:>+9.1f}%{r['efecto_volumen_M']:>17,.1f}{r['efecto_volumen_pct']:>9.1f}%")

# ─── 1.bis PRECIO PROMEDIO: EFECTO MEZCLA vs. PRECIO DENTRO DE CADA RUBRO ───
# El precio implícito total (Fase 4.1) puede subir solo porque cambia la composición
# (más MOA, que vale ~4x por tonelada) aunque el precio de cada rubro baje.
g = df.groupby(["Año", "Rubro"])[["FOB_dólar", "Peso neto"]].sum()

def tabla_rubros(año: int) -> pd.DataFrame:
    t = g.loc[año].copy()
    t["ton"] = t["Peso neto"] / 1000
    t = t[t["ton"] > 0]
    t["precio"] = t["FOB_dólar"] / t["ton"]
    t["share_ton"] = t["ton"] / t["ton"].sum()
    return t

def mezcla_vs_precio(año0: int, año1: int) -> tuple[float, float, float, float]:
    t0, t1 = tabla_rubros(año0), tabla_rubros(año1)
    rubros = t0.index.intersection(t1.index)
    mezcla = sum((t1.loc[r, "share_ton"] - t0.loc[r, "share_ton"]) * t0.loc[r, "precio"] for r in rubros)
    interno = sum(t1.loc[r, "share_ton"] * (t1.loc[r, "precio"] - t0.loc[r, "precio"]) for r in rubros)
    p0 = t0["FOB_dólar"].sum() / t0["ton"].sum()
    p1 = t1["FOB_dólar"].sum() / t1["ton"].sum()
    return p0, p1, mezcla, interno

p0, p1, mezcla, interno = mezcla_vs_precio(2022, 2024)
print("\n" + "=" * 92)
print("PRECIO PROMEDIO 2022→2024: ¿MEZCLA DE RUBROS O PRECIO REAL?")
print("=" * 92)
print(f"Precio promedio total: {p0:,.1f} → {p1:,.1f} USD/ton ({p1 - p0:+,.1f})")
print(f"  Efecto mezcla de rubros:            {mezcla:+,.1f} USD/ton")
print(f"  Efecto precio dentro de cada rubro: {interno:+,.1f} USD/ton")

# ─── 2. TABLERO FINAL: RESUMEN DE TODOS LOS FACTORES EVALUADOS EN LA FASE 4 ─
print("\n\n" + "=" * 92)
print("📋 TABLERO RESUMEN — OBJETIVO #4 (todos los factores evaluados, Fases 4.1-4.8)")
print("=" * 92)

tablero = [
    ("Precio promedio de Chaco (todos los rubros juntos)", "4.1",
     "Subió +12,4% (2022→2024), pero por efecto MEZCLA (+89,8 USD/ton, más MOA); "
     "dentro de cada rubro el precio bajó (PP -9,5%, MOA -7,7%)",
     "ENGAÑOSO — el promedio sube por composición, no por precio"),
    ("Precio dentro de cada rubro", "4.9",
     "El precio por tonelada de PP cayó -9,5%, pero el volumen explica 95,4% de la caída de PP",
     "SECUNDARIO — contribuyó, no explica"),
    ("Volumen exportado (toneladas)", "4.3 / 4.9",
     "Explica 86%-159% del Δ USD en los 5 tramos analizados",
     "COMPONENTE DOMINANTE (describe qué se movió, no por qué)"),
    ("Precio internacional (proxy: soja cruda)", "4.4",
     "Correlación 0,86 (2002-2025). Entre 2022 y 2024 la soja cayó -26,7% y el precio de PP -9,5%",
     "NO EXPLICA LA MAGNITUD — misma dirección, mucha menos caída en Chaco"),
    ("Tipo de cambio real (ITCRM)", "4.5",
     "Casi no se movió 2022-2024 (+0,2%); correlación moderada y de signo contrario (-0,64 en 2002-2026; -0,37 en 2015-2025)",
     "DESCARTADO para 2022-2024 (el índice no se movió)"),
    ("Composición por Rubro (PP vs. MOA)", "4.6",
     "PP perdió 24 pp de participación (89,4%→65,4%); MOA ganó 23,1 pp",
     "CONFIRMADO — localiza dónde ocurrió el cambio (no es una causa en sí)"),
    ("Retenciones (sobre la CAÍDA 2022-2024)", "4.8",
     "La cronología (retenciones_chaco.csv) arranca en ene-2025; no hay datos de cambios de alícuota en 2022-2024",
     "NO EVALUABLE con estos datos"),
    ("Retenciones (sobre la RECUPERACIÓN 2025-2026)", "4.8",
     "Único tramo con decretos vigentes; sin señal clara en volumen mensual agregado (total ni PP)",
     "NO CONCLUYENTE — evidencia indirecta de efecto en timing, no en volumen"),
]

for factor, fase, evidencia, veredicto in tablero:
    print(f"\n• {factor} (Fase {fase})")
    print(f"    Evidencia: {evidencia}")
    print(f"    Veredicto: {veredicto}")

print("\n" + "=" * 92)
print("📌 SÍNTESIS")
print("=" * 92)
print("La caída 2022-2024 y la recuperación 2026 de Chaco se explican sobre todo por")
print("VOLUMEN, no por precio. El precio promedio sube por efecto mezcla (más MOA);")
print("dentro de cada rubro cae entre 8% y 10%, un aporte menor frente al volumen")
print("(95,4% de la caída de PP). Ese volumen no se movió parejo: se concentró en")
print("Productos Primarios, mientras MOA creció. El tipo de cambio real no se movió")
print("entre 2022 y 2024. Las retenciones no pueden evaluarse contra la caída (la")
print("cronología arranca en 2025) y, contra la recuperación, no muestran efecto claro")
print("sobre el volumen mensual agregado, con evidencia indirecta de efecto en el")
print("momento de venta (cupo de DJVE agotado en 3 días en sep-2025).")
print("=" * 92)