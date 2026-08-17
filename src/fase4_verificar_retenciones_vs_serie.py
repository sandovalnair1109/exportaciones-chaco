"""
Fase 4.8.b — Verificar si hay señal en la serie mensual de Chaco
alrededor de los cambios de retenciones
Fuentes:
    - data/processed/chaco_serie_mensual_2002_2026.csv
    - data/raw/retenciones_chaco.csv

Qué hace (y qué NO hace) este paso:
    Es un chequeo PUNTUAL, no el cruce completo (eso es 4.8.c). La idea es
    simple: ¿los meses donde cambió una alícuota de retención muestran algo
    fuera de lo normal en la serie de Chaco (FOB o toneladas), comparado
    contra el mismo mes del año anterior? Si NO hay nada raro en ningún mes,
    no tiene sentido invertir tiempo en el gráfico completo de 4.8.c. Si SÍ
    hay señal en algún punto, ahí se justifica el análisis más profundo.

    Esto NO prueba causalidad ni descarta otras causas (estacionalidad
    normal, clima, logística) — solo dice "acá pasa algo que vale la pena
    mirar con más cuidado" o "acá no pasa nada especial".

Meses analizados: todos los meses de 2025 y el primer semestre de 2026,
comparados contra el mismo mes del año anterior — no solo los meses donde
hubo un decreto nuevo, para no sesgar la búsqueda mirando solo donde
"se espera" encontrar algo.

Uso desde notebook:
    %run ../src/fase4_verificar_retenciones_vs_serie.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO_CHACO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"
ARCHIVO_RETENCIONES = RAIZ / "data" / "raw" / "retenciones_chaco.csv"

# ─── 1. SERIE MENSUAL TOTAL DE CHACO (todos los rubros sumados) ────────────
df = pd.read_csv(ARCHIVO_CHACO)
mensual = df.groupby(["Año", "Mes"])[["FOB_dólar", "Peso neto"]].sum().reset_index()
mensual = mensual.sort_values(["Año", "Mes"]).reset_index(drop=True)

# Variación interanual: mismo mes, año anterior
mensual["fob_año_anterior"] = mensual.set_index(["Año", "Mes"]).index.map(
    lambda idx: mensual.loc[
        (mensual["Año"] == idx[0] - 1) & (mensual["Mes"] == idx[1]), "FOB_dólar"
    ].squeeze() if not mensual.loc[
        (mensual["Año"] == idx[0] - 1) & (mensual["Mes"] == idx[1])
    ].empty else None
)
mensual["ton_año_anterior"] = mensual.set_index(["Año", "Mes"]).index.map(
    lambda idx: mensual.loc[
        (mensual["Año"] == idx[0] - 1) & (mensual["Mes"] == idx[1]), "Peso neto"
    ].squeeze() if not mensual.loc[
        (mensual["Año"] == idx[0] - 1) & (mensual["Mes"] == idx[1])
    ].empty else None
)
mensual["var_fob_interanual_pct"] = (
    (mensual["FOB_dólar"] - mensual["fob_año_anterior"]) / mensual["fob_año_anterior"] * 100
)
mensual["var_ton_interanual_pct"] = (
    (mensual["Peso neto"] - mensual["ton_año_anterior"]) / mensual["ton_año_anterior"] * 100
)

# ─── 2. FECHAS DE CAMBIO DE RETENCIONES (a nivel decreto, no producto) ──────
retenciones = pd.read_csv(ARCHIVO_RETENCIONES, sep=";")
retenciones["fecha_inicio_dt"] = pd.to_datetime(retenciones["fecha_inicio"])
fechas_cambio = sorted(retenciones["fecha_inicio_dt"].unique())

meses_con_cambio = sorted({(f.year, f.month) for f in fechas_cambio})

print("=" * 90)
print("FASE 4.8.b — ¿HAY SEÑAL EN LA SERIE MENSUAL ALREDEDOR DE LOS CAMBIOS DE RETENCIONES?")
print("=" * 90)
print(f"\nMeses con al menos un decreto nuevo entrando en vigencia: {meses_con_cambio}")

# ─── 3. TABLA COMPLETA: TODOS LOS MESES DE 2025-2026, CON MARCA DE CAMBIO ───
ventana = mensual[(mensual["Año"] >= 2025)].copy()
ventana["hay_cambio_retencion"] = ventana.apply(
    lambda r: (int(r["Año"]), int(r["Mes"])) in meses_con_cambio, axis=1
)

print(f"\n{'Año-Mes':<10}{'FOB (M USD)':>14}{'Δ% interanual':>16}{'Toneladas':>14}{'Δ% interanual':>16}{'¿Cambio retención?':>20}")
print("-" * 90)
for _, row in ventana.iterrows():
    fob_m = row["FOB_dólar"] / 1e6
    ton = row["Peso neto"] / 1000
    var_fob = f"{row['var_fob_interanual_pct']:+.1f}%" if pd.notna(row["var_fob_interanual_pct"]) else "—"
    var_ton = f"{row['var_ton_interanual_pct']:+.1f}%" if pd.notna(row["var_ton_interanual_pct"]) else "—"
    marca = "🔶 SÍ" if row["hay_cambio_retencion"] else ""
    print(f"{int(row['Año'])}-{int(row['Mes']):02d}   {fob_m:>14,.1f}{var_fob:>16}{ton:>14,.0f}{var_ton:>16}{marca:>20}")

# ─── 4. COMPARAR: ¿LOS MESES CON CAMBIO SON MÁS EXTREMOS QUE LOS MESES SIN CAMBIO? ──
con_cambio = ventana[ventana["hay_cambio_retencion"]]["var_fob_interanual_pct"].dropna()
sin_cambio = ventana[~ventana["hay_cambio_retencion"]]["var_fob_interanual_pct"].dropna()

print("\n" + "=" * 90)
print("📊 COMPARACIÓN: ¿LOS MESES CON CAMBIO DE RETENCIÓN SON MÁS VOLÁTILES?")
print("=" * 90)
print(f"Meses CON cambio de retención — variación interanual promedio:  {con_cambio.mean():+.1f}%  "
      f"(desvío: {con_cambio.std():.1f}, n={len(con_cambio)})")
print(f"Meses SIN cambio de retención — variación interanual promedio:  {sin_cambio.mean():+.1f}%  "
      f"(desvío: {sin_cambio.std():.1f}, n={len(sin_cambio)})")

print("\n" + "=" * 90)
print("📌 CONCLUSIÓN DEL CHEQUEO (todavía sin interpretar causalidad)")
print("=" * 90)
diferencia_promedios = abs(con_cambio.mean() - sin_cambio.mean())
if diferencia_promedios > 15:
    print(f"✅ HAY SEÑAL: los meses con cambio de retención muestran una variación")
    print(f"   interanual bastante distinta a los meses sin cambio (diferencia de "
          f"{diferencia_promedios:.1f} puntos porcentuales en el promedio).")
    print("   → Justifica avanzar a la Fase 4.8.c (cruce completo con gráfico).")
else:
    print(f"⚠️  SEÑAL DÉBIL: la diferencia entre meses con y sin cambio de retención")
    print(f"    es de solo {diferencia_promedios:.1f} puntos porcentuales — no hay un")
    print("    patrón claro a simple vista con este corte mensual agregado.")
    print("   → Revisar caso por caso antes de invertir en el cruce completo de 4.8.c,")
    print("     o considerar que el efecto (si existe) se diluye al mirar el total de")
    print("     Chaco en vez de solo los productos específicamente afectados por cada")
    print("     decreto (soja/trigo/maíz-sorgo, no el total que incluye MOA/MOI/CyE).")
print("=" * 90)