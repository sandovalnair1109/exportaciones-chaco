"""
Paso 1 (Fase 1.2) — Chequeo de calidad del dataset de Chaco
Fuente: data/processed/chaco_serie_mensual_2002_2026.csv

Este script es un WRAPPER de las funciones genéricas de data_quality.py,
no una reimplementación. Existe porque data_quality.py fue diseñado como
herramienta de línea de comandos (recibe la ruta como argumento), lo cual
no encaja con el patrón `%run ../src/archivo.py` sin argumentos que usan
los demás notebooks del proyecto.

Además resuelve un problema de orden: chequeo_completitud_temporal()
necesita UNA columna de fecha, pero el dataset trae 'Año' y 'Mes' por
separado (esa unificación formal es la Fase 1.3, todavía no ejecutada).
Acá se arma una columna de fecha SOLO EN MEMORIA, únicamente para poder
correr el chequeo de huecos temporales ahora — no se persiste en el CSV.

Uso desde notebook:
    %run ../src/chequeo_calidad_chaco.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_quality import (
    resumen_estructura,
    chequeo_valores_faltantes,
    chequeo_duplicados,
    chequeo_completitud_temporal,
)

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "processed" / "chaco_serie_mensual_2002_2026.csv"

# Columnas que definen un registro único en este dataset: un mes puede tener
# varias filas (una por Rubro), así que el duplicado real se chequea sobre
# la combinación Año+Mes+Rubro, no sobre la fila completa.
COLUMNAS_CLAVE = ["Año", "Mes", "Rubro"]

# ─── CARGA ───────────────────────────────────────────────────────────────────
df = pd.read_csv(ARCHIVO)

print("=" * 70)
print("PASO 1 (Fase 1.2) — CHEQUEO DE CALIDAD")
print("Provincia: Chaco")
print(f"Fuente: {ARCHIVO.name}")
print("=" * 70)

resumen_estructura(df)

print("\n" + "=" * 60)
print("VALORES FALTANTES POR COLUMNA")
print("=" * 60)
print(chequeo_valores_faltantes(df).to_string(index=False))

print("\n" + "=" * 60)
print("DUPLICADOS")
print("=" * 60)
print(f"Filas duplicadas (fila completa): {chequeo_duplicados(df)}")
print(f"Duplicados sobre clave {COLUMNAS_CLAVE}: {chequeo_duplicados(df, COLUMNAS_CLAVE)}")

# ─── COMPLETITUD TEMPORAL (fecha armada solo en memoria) ────────────────────
print("\n" + "=" * 60)
print("COMPLETITUD TEMPORAL")
print("=" * 60)
print("Nota: 'fecha' se arma acá temporalmente (Año+Mes → datetime) solo para")
print("este chequeo. La columna formal se crea recién en la Fase 1.3.\n")

df_temporal = df.copy()
df_temporal["fecha"] = pd.to_datetime(
    df_temporal["Año"].astype(str) + "-" + df_temporal["Mes"].astype(str) + "-01"
)

huecos = chequeo_completitud_temporal(df_temporal, "fecha", frecuencia="MS")
if huecos:
    print(f"Períodos faltantes ({len(huecos)}): {huecos}")
else:
    inicio = df_temporal["fecha"].min().strftime("%Y-%m")
    fin = df_temporal["fecha"].max().strftime("%Y-%m")
    print(f"No se detectaron huecos en la serie temporal ({inicio} a {fin}).")
    
print("\n" + "=" * 70)
print("📌 CONCLUSIÓN")
print("=" * 70)
print("Dataset sin nulos, sin duplicados por clave, sin huecos temporales.")
print("Listo para construir la columna de fecha formal (Fase 1.3) y seguir")
print("con el resto de la Fase 1.")
print("=" * 70)