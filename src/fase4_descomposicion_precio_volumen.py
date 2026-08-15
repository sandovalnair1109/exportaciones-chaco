"""
Fase 4.3 — Descomposición explícita: ¿la caída y la recuperación se explican
por volumen o por precio?
Fuente: data/processed/chaco_serie_mensual_2002_2026.csv

Las Fases 4.1 y 4.2 ya mostraron, de forma descriptiva, que el precio
implícito NO cayó entre 2022 y 2024 (subió). Este paso lo formaliza con
una descomposición contable estándar, para poder decir con un número
exacto (no solo "parece que es volumen") qué parte de cada variación en
USD responde a precio y qué parte a volumen.

Método (descomposición exacta de dos factores):
    Valor = Precio × Volumen
    ΔValor = (P1 - P0) × Q0   →  efecto_precio  (variación de precio, al volumen inicial)
           + (Q1 - Q0) × P0   →  efecto_volumen (variación de volumen, al precio inicial)
           + (P1-P0)×(Q1-Q0)  →  efecto_interacción (parte que no se puede
                                   atribuir limpiamente a uno solo de los dos,
                                   porque ambos cambiaron a la vez)

Los tres términos suman EXACTO el ΔValor total (no es una aproximación).
Es la misma lógica que un análisis de varianza precio-volumen en costos o
en ventas.

Uso desde notebook:
    %run ../src/fase4_descomposicion_precio_volumen.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"

df = pd.read_csv(ARCHIVO)

# ─── AGREGACIÓN ANUAL (misma base que Fase 4.1) ─────────────────────────────
anual = df.groupby("Año")[["FOB_dólar", "Peso neto"]].sum()
anual["toneladas"] = anual["Peso neto"] / 1000
anual["precio_usd_ton"] = anual["FOB_dólar"] / anual["toneladas"]


def descomponer(año0: int, año1: int, tabla: pd.DataFrame = anual) -> dict:
    """
    Descompone el cambio en FOB_dólar entre año0 y año1 en efecto precio,
    efecto volumen y efecto interacción (en USD y en % del ΔValor total).
    """
    p0, p1 = tabla.loc[año0, "precio_usd_ton"], tabla.loc[año1, "precio_usd_ton"]
    q0, q1 = tabla.loc[año0, "toneladas"], tabla.loc[año1, "toneladas"]
    v0, v1 = tabla.loc[año0, "FOB_dólar"], tabla.loc[año1, "FOB_dólar"]

    delta_total = v1 - v0
    efecto_precio = (p1 - p0) * q0
    efecto_volumen = (q1 - q0) * p0
    efecto_interaccion = (p1 - p0) * (q1 - q0)

    # Chequeo de identidad contable: los tres términos deben sumar el total exacto
    suma = efecto_precio + efecto_volumen + efecto_interaccion
    assert abs(suma - delta_total) < 1, (
        f"La descomposición no cierra para {año0}->{año1}: "
        f"suma={suma:,.2f} vs delta_total={delta_total:,.2f}"
    )

    return {
        "periodo": f"{año0} → {año1}",
        "valor_usd_0": v0,
        "valor_usd_1": v1,
        "delta_total_usd": delta_total,
        "delta_total_pct": delta_total / v0 * 100,
        "efecto_precio_usd": efecto_precio,
        "efecto_precio_pct_del_delta": efecto_precio / delta_total * 100,
        "efecto_volumen_usd": efecto_volumen,
        "efecto_volumen_pct_del_delta": efecto_volumen / delta_total * 100,
        "efecto_interaccion_usd": efecto_interaccion,
        "efecto_interaccion_pct_del_delta": efecto_interaccion / delta_total * 100,
    }


def imprimir_descomposicion(resultado: dict) -> None:
    print(f"\n{'─'*74}")
    print(f"  {resultado['periodo']}")
    print(f"{'─'*74}")
    print(f"  Valor inicial:  USD {resultado['valor_usd_0']/1e6:>8,.1f} M")
    print(f"  Valor final:    USD {resultado['valor_usd_1']/1e6:>8,.1f} M")
    print(f"  Δ Total:        USD {resultado['delta_total_usd']/1e6:>+8,.1f} M  ({resultado['delta_total_pct']:+.1f}%)")
    print()
    print(f"  {'Efecto':<20}{'USD (millones)':>18}{'% del Δ total':>18}")
    print(f"  {'-'*56}")
    print(f"  {'Precio':<20}{resultado['efecto_precio_usd']/1e6:>18,.1f}{resultado['efecto_precio_pct_del_delta']:>17.1f}%")
    print(f"  {'Volumen':<20}{resultado['efecto_volumen_usd']/1e6:>18,.1f}{resultado['efecto_volumen_pct_del_delta']:>17.1f}%")
    print(f"  {'Interacción':<20}{resultado['efecto_interaccion_usd']/1e6:>18,.1f}{resultado['efecto_interaccion_pct_del_delta']:>17.1f}%")


# ─── BLOQUE 1: LA CAÍDA, AÑO A AÑO (2022→2023→2024) ─────────────────────────
print("=" * 74)
print("FASE 4.3 — DESCOMPOSICIÓN PRECIO vs. VOLUMEN")
print("Provincia: Chaco")
print("=" * 74)

print("\n📉 BLOQUE 1 — LA CAÍDA (años completos, año a año)")
resultados_caida = []
for año0, año1 in [(2022, 2023), (2023, 2024), (2022, 2024)]:
    r = descomponer(año0, año1)
    resultados_caida.append(r)
    imprimir_descomposicion(r)

# ─── BLOQUE 2: LA RECUPERACIÓN 2024→2025→2026 ───────────────────────────────
# 2026 es parcial (6 meses) — comparar contra el año completo 2025 distorsiona
# el efecto volumen (2026 arrancaría "perdiendo" la mitad del año que ni
# transcurrió). Por eso 2024→2025 se hace con años completos, pero la
# recuperación 2025→2026 se hace comparando el MISMO recorte de calendario
# (primer semestre) en ambos años, igual que la Fase 1.11.
print("\n\n📈 BLOQUE 2 — LA RECUPERACIÓN")

r_2024_2025 = descomponer(2024, 2025)
imprimir_descomposicion(r_2024_2025)

primer_semestre = df[df["Mes"] <= 6].groupby("Año")[["FOB_dólar", "Peso neto"]].sum()
primer_semestre["toneladas"] = primer_semestre["Peso neto"] / 1000
primer_semestre["precio_usd_ton"] = primer_semestre["FOB_dólar"] / primer_semestre["toneladas"]

r_h1_2025_2026 = descomponer(2025, 2026, tabla=primer_semestre)
r_h1_2025_2026["periodo"] = "2025 → 2026 (solo primer semestre, Ene-Jun, para comparar años iguales)"
imprimir_descomposicion(r_h1_2025_2026)

# ─── TABLA RESUMEN ───────────────────────────────────────────────────────────
print("\n\n" + "=" * 74)
print("📊 RESUMEN — ¿QUÉ EFECTO DOMINA EN CADA TRAMO?")
print("=" * 74)
print(f"{'Período':<45}{'Δ Total (M USD)':>15}{'Efecto dominante':>16}")
print("-" * 76)

todos = resultados_caida + [r_2024_2025, r_h1_2025_2026]
for r in todos:
    efectos = {
        "Precio": r["efecto_precio_pct_del_delta"],
        "Volumen": r["efecto_volumen_pct_del_delta"],
        "Interacción": r["efecto_interaccion_pct_del_delta"],
    }
    dominante = max(efectos, key=lambda k: abs(efectos[k]))
    print(f"{r['periodo']:<45}{r['delta_total_usd']/1e6:>+15,.1f}{dominante:>16}")

print("\n" + "=" * 74)
print("📌 NOTA METODOLÓGICA")
print("=" * 74)
print("El 'efecto interacción' no es un error de cálculo ni un residuo: es la")
print("parte del cambio que ocurre porque precio Y volumen se movieron a la vez")
print("en la misma dirección (o en direcciones opuestas). Cuando es chico en")
print("relación al total, es señal de que un solo factor domina con claridad.")
print("Cuando es grande, señala que ambos factores se movieron juntos de forma")
print("relevante y no conviene simplificar la historia a un solo causante.")
print("=" * 74)