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

# ─── 2. TABLERO FINAL: RESUMEN DE TODOS LOS FACTORES EVALUADOS EN LA FASE 4 ─
print("\n\n" + "=" * 92)
print("📋 TABLERO RESUMEN — OBJETIVO #4 (todos los factores evaluados, Fases 4.1-4.8)")
print("=" * 92)

tablero = [
    ("Precio implícito propio (Chaco, todos los rubros)", "4.1",
     "Subió +12,4% (2022→2024), no cayó", "DESCARTADO"),
    ("Volumen exportado (toneladas)", "4.3",
     "Explica 87%-160% del Δ USD en los 5 tramos analizados", "CONFIRMADO — causa principal"),
    ("Precio internacional (proxy: soja cruda)", "4.4",
     "Correlación 0,86 en 2015-2025, pero se desacopla justo en 2024 (-20,7% soja vs. +15,1% Chaco)", "DESCARTADO"),
    ("Tipo de cambio real (ITCRM)", "4.5",
     "Casi no se movió 2022-2024 (+0,2%); correlación débil y de signo contrario (-0,64) en toda la serie", "DESCARTADO"),
    ("Composición por Rubro (PP vs. MOA)", "4.6",
     "PP perdió 24 pp de participación (89,4%→65,4%); MOA ganó 23,1 pp", "CONFIRMADO — explica el patrón del volumen"),
    ("Retenciones (efecto sobre la CAÍDA 2022-2024)", "4.8",
     "Cronología disponible arranca en ene-2025 (decreto 38/2025) — posterior al 100% de la caída "
     "de PP (461,7M→140,8M ya consumado para fines de 2024)", "NO APLICA — desfasaje temporal, no pudo haber sido causa"),
    ("Retenciones (efecto sobre la RECUPERACIÓN 2025-2026)", "4.8",
     "Único tramo donde hay decretos vigentes; sin señal clara en volumen mensual agregado (total ni PP)",
     "NO CONCLUYENTE — evidencia indirecta de efecto en timing, no en volumen"),
]

for factor, fase, evidencia, veredicto in tablero:
    print(f"\n• {factor} (Fase {fase})")
    print(f"    Evidencia: {evidencia}")
    print(f"    Veredicto: {veredicto}")

print("\n" + "=" * 92)
print("📌 SÍNTESIS")
print("=" * 92)
print("La caída 2022-2024 y la recuperación 2026 de Chaco se explican por VOLUMEN,")
print("no por precio — y ese volumen no cayó/subió parejo: se concentró en Productos")
print("Primarios, mientras Manufacturas de origen agropecuario creció en el mismo")
print("período. Ni el precio internacional de referencia (soja) ni el tipo de cambio")
print("real (ITCRM) acompañan el movimiento cuando más se los necesita (2022-2024).")
print("Las retenciones NO pudieron ser causa de la caída 2022-2024: la cronología")
print("disponible arranca en enero de 2025, cuando el 100% de esa caída ya había")
print("ocurrido. Contra la recuperación 2025-2026 —el único tramo donde sí aplican—")
print("no muestran un efecto claro sobre el volumen agregado mensual, aunque hay")
print("evidencia indirecta de que afectan el momento de venta dentro del año")
print("(cupo de DJVE agotado en 3 días en sep-2025).")
print("=" * 92)