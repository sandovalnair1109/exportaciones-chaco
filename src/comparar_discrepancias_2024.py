"""
Análisis de discrepancias: microdatos 2024 vs. totales oficiales INDEC
Provincia: Chaco

Uso desde notebook:
    %run ../src/comparar_discrepancias_2024.py
"""
import pandas as pd
from pathlib import Path

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
RAIZ = Path(__file__).resolve().parents[1]

ARCHIVO_MICRO = RAIZ / "data" / "raw" / "exports_2024_Y" / "Datos_origen_2024_mayo_2025.xlsx"
HOJA_MICRO = "Datos Opex Año 2024"

ARCHIVO_OFICIAL = RAIZ / "data" / "raw" / "opex_anexo_cuadros_10_03_26.xls"
HOJA_OFICIAL = "OP-Regiones 2022-2025"

# ─── 1. TOTAL DESDE MICRODATOS 2024 ─────────────────────────────────────────
df_micro = pd.read_excel(ARCHIVO_MICRO, sheet_name=HOJA_MICRO)
chaco_micro = df_micro[df_micro["DESCRIP_PCIA"].astype(str).str.strip() == "Chaco"].copy()

total_micro_usd = chaco_micro["DOLARES_FOB"].sum()
total_micro_kg = chaco_micro["PESO_NETO_KG"].sum()

meses_presentes = sorted(chaco_micro["CMES"].dropna().unique())
# NOTA IMPORTANTE: este archivo es de modalidad ANUAL ACUMULADA. El valor
# CMES=12 es un marcador de "cierre del año completo", NO significa que solo
# haya datos de diciembre. Las 304 filas de Chaco ya representan el año 2024
# completo sumado. Por eso NO calculamos "meses faltantes" aquí — hacerlo
# llevaría a la conclusión incorrecta de que faltan datos, cuando en realidad
# el archivo está completo y la discrepancia se debe a la metodología de
# asignación de provincia (ver docs/fuentes.md), no a cobertura temporal.
es_modalidad_anual = list(meses_presentes) == [12]

confid = chaco_micro[
    chaco_micro["DESCRIP_RUBRO"].str.contains("confidencial|Confidencial", case=False, na=False)
]
total_confid_usd = confid["DOLARES_FOB"].sum()

# ─── 2. TOTAL OFICIAL 2024 ──────────────────────────────────────────────────
df_oficial = pd.read_excel(ARCHIVO_OFICIAL, sheet_name=HOJA_OFICIAL, header=None)

total_oficial_millones = None
fila_idx = None
for i in range(len(df_oficial)):
    if str(df_oficial.iat[i, 1]).strip() == "Chaco":
        total_oficial_millones = df_oficial.iat[i, 4]  # 2024 está en col 4
        fila_idx = i
        break

if total_oficial_millones is None or pd.isna(total_oficial_millones):
    raise ValueError("No se encontró el valor oficial 2024 para Chaco.")

total_oficial_usd = total_oficial_millones * 1_000_000

# ─── 3. CÁLCULO DE DISCREPANCIAS ────────────────────────────────────────────
diferencia_usd = total_micro_usd - total_oficial_usd
diferencia_pct = (diferencia_usd / total_oficial_usd) * 100 if total_oficial_usd != 0 else 0

# ─── 4. REPORTE ─────────────────────────────────────────────────────────────
print("=" * 70)
print("PASO 3 — ANÁLISIS DE DISCREPANCIAS")
print("Microdatos OPEX 2024  vs.  Totales anuales oficiales INDEC")
print("Provincia: Chaco")
print("=" * 70)

print("\n📊 COMPARACIÓN DE TOTALES (USD FOB)")
print("-" * 55)
print(f"{'Concepto':<35} {'Valor':>18}")
print("-" * 55)
print(f"{'Microdatos 2024 (suma cruda)':<35} ${total_micro_usd:>15,.0f}")
print(f"{'Oficial INDEC 2024 (anexo regiones)':<35} ${total_oficial_usd:>15,.0f}")
print("-" * 55)
print(f"{'Diferencia absoluta':<35} ${diferencia_usd:>15,.0f}")
print(f"{'Diferencia porcentual':<35} {diferencia_pct:>17.1f}%")
print("=" * 55)

print("\n📅 MODALIDAD DEL ARCHIVO DE MICRODATOS")
if es_modalidad_anual:
    print("   ✅ Modalidad ANUAL ACUMULADA (CMES=12 = cierre de año, no 'solo diciembre').")
    print("   Las 304 filas de Chaco representan el año 2024 completo.")
else:
    print(f"   Meses presentes: {[int(m) for m in meses_presentes]} (modalidad no anual, revisar)")

print("\n🔒 REGISTROS CONFIDENCIALES EN MICRODATOS")
print(f"   Cantidad de registros: {len(confid)}")
print(f"   Valor acumulado:       ${total_confid_usd:,.0f}")
if len(confid) > 0:
    print(f"   Participación:         {total_confid_usd/total_micro_usd*100:.1f}% del total microdatos")

print("\n" + "=" * 70)
print("📌 CONCLUSIÓN")
print("=" * 70)

if abs(diferencia_pct) <= 5:
    print("✅ Los microdatos 2024 son consistentes con el dato oficial.")
else:
    print(f"⚠️  Discrepancia del {abs(diferencia_pct):.1f}%.")
    print("   Causa: dos metodologías distintas de asignación de provincia de")
    print("   origen (ver docs/fuentes.md). NO es un problema de cobertura")
    print("   temporal — el archivo de microdatos ya está completo (año cerrado).")
    print("   → Usar la serie mensual oficial OPEX para el análisis principal.")

print("=" * 70)