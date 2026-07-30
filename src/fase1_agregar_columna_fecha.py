"""
Paso 2 (Fase 1.3) — Agregar columna de fecha persistente
Fuente/destino: data/processed/chaco_serie_mensual_2002_2026.csv

A diferencia de chequeo_calidad_chaco.py (Fase 1.2), acá la columna
'fecha' se guarda de forma permanente en el CSV, para no tener que
reconstruirla en cada notebook de las fases siguientes.

Uso desde notebook:
    %run ../src/agregar_columna_fecha.py
"""
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"

df = pd.read_csv(ARCHIVO)
df["fecha"] = pd.to_datetime(
    df["Año"].astype(str) + "-" + df["Mes"].astype(str) + "-01"
)
df.to_csv(ARCHIVO, index=False)

print(f"Columna 'fecha' agregada y persistida en: {ARCHIVO.name}")
print(f"Rango: {df['fecha'].min().strftime('%Y-%m')} a {df['fecha'].max().strftime('%Y-%m')}")
print(f"Filas: {len(df)} | Columnas: {list(df.columns)}")