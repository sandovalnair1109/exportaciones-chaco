"""
Paso 5 — Validación final del dataset procesado de Chaco
Fuente: data/processed/chaco_serie_mensual_2002_2026.csv
(resultado de filtrar_provincia.py sobre Serie_Opex_Mensual_2002_2026.xlsx)

Este es el último chequeo de la Fase 0, antes de arrancar la Fase 1. No
vuelve a comparar contra el oficial (eso ya lo hizo verificar_primer_semestre.py
y comparar_discrepancias_2024.py) — acá el objetivo es distinto: confirmar
que el ARCHIVO PROCESADO que vamos a usar de acá en adelante está completo,
bien tipado y listo para analizar, y dejar un registro reproducible de eso.

Uso desde la terminal:
    python src/validar_dataset_procesado.py
Uso desde notebook:
    %run ../src/validar_dataset_procesado.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_quality import (
    chequeo_valores_faltantes,
    chequeo_duplicados,
)

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"

COLUMNAS_ESPERADAS = [
    "Año", "Mes", "FOB_dólar", "Peso neto",
    "Nombre Prov", "Nombre_Región", "Rubro",
]
FILAS_ESPERADAS = 884  # confirmado en Fase 0.9 al filtrar por Chaco

# ─── CARGA ───────────────────────────────────────────────────────────────────
df = pd.read_csv(ARCHIVO)

print("=" * 70)
print("PASO 5 — VALIDACIÓN FINAL DEL DATASET PROCESADO")
print("Provincia: Chaco")
print(f"Fuente: {ARCHIVO.name}")
print("=" * 70)

# ─── 1. ESTRUCTURA ───────────────────────────────────────────────────────────
print("\n📐 ESTRUCTURA")
print("-" * 50)
print(f"Filas:    {len(df)}  (esperadas: {FILAS_ESPERADAS})")
print(f"Columnas: {list(df.columns)}")

columnas_faltantes = set(COLUMNAS_ESPERADAS) - set(df.columns)
columnas_extra = set(df.columns) - set(COLUMNAS_ESPERADAS)

ok_filas = len(df) == FILAS_ESPERADAS
ok_columnas = not columnas_faltantes

print(f"\n{'✅' if ok_filas else '⚠️ '} Cantidad de filas {'coincide' if ok_filas else 'NO coincide'} con lo esperado")
print(f"{'✅' if ok_columnas else '❌'} Columnas {'completas' if ok_columnas else 'FALTAN: ' + str(columnas_faltantes)}")
if columnas_extra:
    print(f"ℹ️  Columnas extra no esperadas (no es un error, solo aviso): {columnas_extra}")

# ─── 2. PROVINCIA ÚNICA ──────────────────────────────────────────────────────
print("\n🗺️  CONSISTENCIA DE PROVINCIA")
print("-" * 50)
provincias = df["Nombre Prov"].unique()
ok_provincia = list(provincias) == ["Chaco"]
print(f"{'✅' if ok_provincia else '❌'} Valores únicos en 'Nombre Prov': {list(provincias)}")

regiones = df["Nombre_Región"].unique()
print(f"   Valores únicos en 'Nombre_Región': {list(regiones)}")

# ─── 3. NULOS Y DUPLICADOS (reutilizando data_quality.py) ──────────────────
print("\n🔍 VALORES FALTANTES")
print("-" * 50)
reporte_nulos = chequeo_valores_faltantes(df)
print(reporte_nulos.to_string(index=False))

duplicados = chequeo_duplicados(df)
print(f"\nFilas completamente duplicadas: {duplicados}")

# ─── 4. COBERTURA TEMPORAL ───────────────────────────────────────────────────
print("\n📅 COBERTURA TEMPORAL")
print("-" * 50)
print(f"Años cubiertos: {df['Año'].min()} - {df['Año'].max()}")
meses_2026 = sorted(df[df["Año"] == 2026]["Mes"].unique())
print(f"Meses disponibles en 2026: {meses_2026}")

# ─── 5. RUBROS ────────────────────────────────────────────────────────────
print("\n🏷️  RUBROS PRESENTES")
print("-" * 50)
for rubro in sorted(df["Rubro"].unique()):
    print(f"  - {rubro}")

# ─── 6. TIPOS DE DATO ─────────────────────────────────────────────────────
print("\n🔢 TIPOS DE DATO")
print("-" * 50)
print(df.dtypes)

# ─── CONCLUSIÓN ───────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("📌 CONCLUSIÓN")
print("=" * 70)
if ok_filas and ok_columnas and ok_provincia and duplicados == 0:
    print("✅ Dataset procesado validado. Listo para la Fase 1.")
else:
    print("⚠️  Hay observaciones arriba — revisar antes de avanzar a la Fase 1.")
print("=" * 70)