"""
Paso 4 — Evaluación de primeros semestres via serie mensual oficial
Fuente: Serie_Opex_Mensual_2002_2026.xlsx
Hoja:   Serie_Opex_Mensual_2002_2026_06

Uso desde la raíz del proyecto:
    python src/verificar_primer_semestre.py
Uso desde notebook:
    %run ../src/verificar_primer_semestre.py
"""
import pandas as pd
from pathlib import Path

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
RAIZ = Path(__file__).resolve().parents[1]

ARCHIVO = RAIZ / "data" / "raw" / "exports_2026_M" / "Serie_Opex_Mensual_2002_2026.xlsx"
HOJA = "Serie_Opex_Mensual_2002_2026_06"

# ─── LECTURA Y FILTRO ───────────────────────────────────────────────────────
df = pd.read_excel(ARCHIVO, sheet_name=HOJA)
df["Año"] = df["Año"].astype(int)
df["Mes"] = df["Mes"].astype(int)

chaco = df[df["Nombre Prov"].astype(str).str.strip() == "Chaco"]
primer_semestre = chaco[chaco["Mes"] <= 6]

# ─── AGREGACIÓN ─────────────────────────────────────────────────────────────
usd = primer_semestre.groupby("Año")["FOB_dólar"].sum() / 1_000_000
ton = primer_semestre.groupby("Año")["Peso neto"].sum() / 1000

resumen = pd.DataFrame({
    "USD FOB (millones)": usd,
    "Toneladas": ton
}).sort_index()

# ─── REPORTE ────────────────────────────────────────────────────────────────
print("=" * 70)
print("PASO 4 — PRIMER SEMESTRE (Ene-Jun) | Serie mensual oficial INDEC")
print("Provincia: Chaco")
print(f"Fuente: {ARCHIVO.name}")
print(f"Hoja:   {HOJA}")
print("=" * 70)

print(f"\n{'Año':<8} {'USD FOB (millones)':>22} {'Toneladas':>20}")
print("-" * 54)
for año, row in resumen.iterrows():
    print(f"{año:<8} {row['USD FOB (millones)']:>22,.1f} {row['Toneladas']:>20,.0f}")
print("-" * 54)
print(f"{'TOTAL':<8} {resumen['USD FOB (millones)'].sum():>22,.1f} {resumen['Toneladas'].sum():>20,.0f}")

# ─── AÑOS RECIENTES (PARA CRUZAR) ───────────────────────────────────────────
recientes = resumen.loc[resumen.index >= 2020]
if not recientes.empty:
    print("\n" + "─" * 54)
    print("AÑOS RECIENTES — útiles para comparar con microdatos u otros anexos:")
    print("─" * 54)
    for año, row in recientes.iterrows():
        print(f"  {año}  →  USD {row['USD FOB (millones)']:>10,.1f} M  |  {row['Toneladas']:>12,.0f} t")

# ─── MÁXIMO HISTÓRICO (para no perderlo de vista entre tantos años) ────────
año_max_usd = resumen["USD FOB (millones)"].idxmax()
valor_max_usd = resumen["USD FOB (millones)"].max()
año_max_ton = resumen["Toneladas"].idxmax()
valor_max_ton = resumen["Toneladas"].max()

usd_2026 = resumen.loc[2026, "USD FOB (millones)"] if 2026 in resumen.index else None
ton_2026 = resumen.loc[2026, "Toneladas"] if 2026 in resumen.index else None

print("\n" + "─" * 54)
print("MÁXIMO HISTÓRICO DE LA SERIE (2002-presente):")
print("─" * 54)
print(f"  En USD FOB:   {año_max_usd}  →  USD {valor_max_usd:,.1f} M")
print(f"  En toneladas: {año_max_ton}  →  {valor_max_ton:,.0f} t")

if usd_2026 is not None:
    diff_usd_pct = (usd_2026 - valor_max_usd) / valor_max_usd * 100
    diff_ton_pct = (ton_2026 - valor_max_ton) / valor_max_ton * 100
    print()
    if año_max_usd == 2026 and año_max_ton == 2026:
        print("  ✅ 2026 ES el máximo histórico de la serie, en ambos indicadores.")
    else:
        print(f"  2026 vs. máximo histórico en USD:   {diff_usd_pct:+.1f}%")
        print(f"  2026 vs. máximo histórico en toneladas: {diff_ton_pct:+.1f}%")
        print("  ⚠️  2026 es una recuperación fuerte, pero NO es (todavía) el")
        print("     máximo histórico de primer semestre en esta serie.")

print("\n" + "=" * 70)
print("📌 NOTA METODOLÓGICA")
print("=" * 70)
print("Esta serie mensual oficial garantiza comparabilidad interanual,")
print("ya que usa el mismo criterio de registro en todos los años.")
print("Se recomienda usar estos valores como serie principal cuando los")
print("microdatos parciales (Paso 1) no coinciden con los totales oficiales.")
print("=" * 70)