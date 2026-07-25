"""
data_quality.py

Funciones para diagnosticar qué tan completos y consistentes están los datos
de exportaciones antes de avanzar al análisis. La idea NO es limpiar todavía
(eso viene después, una vez que sabemos qué está roto), sino generar un
reporte claro de completitud.

Uso:
    python src/data_quality.py data/raw/indec_exportaciones_chaco.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def cargar_dataset(path: str | Path) -> pd.DataFrame:
    """Carga un CSV o Excel y devuelve un DataFrame, sin modificar nada."""
    path = Path(path)
    if path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    return df


def resumen_estructura(df: pd.DataFrame) -> None:
    """Muestra forma, columnas y tipos de dato del dataset."""
    print("=" * 60)
    print("ESTRUCTURA DEL DATASET")
    print("=" * 60)
    print(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
    print("\nColumnas y tipos de dato:")
    print(df.dtypes)
    print("\nPrimeras filas:")
    print(df.head())


def chequeo_valores_faltantes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve una tabla con cantidad y porcentaje de valores nulos por columna.
    Un porcentaje alto en una columna clave (ej. 'toneladas' o 'provincia')
    es una alerta temprana de que esa columna no sirve como está.
    """
    faltantes = df.isnull().sum()
    porcentaje = (faltantes / len(df) * 100).round(2)
    reporte = pd.DataFrame({
        "columna": df.columns,
        "faltantes": faltantes.values,
        "porcentaje_faltante": porcentaje.values,
    }).sort_values("porcentaje_faltante", ascending=False)
    return reporte


def chequeo_duplicados(df: pd.DataFrame, columnas_clave: list[str] | None = None) -> int:
    """
    Cuenta filas duplicadas. Si se pasan columnas_clave (ej. ['provincia', 'periodo']),
    chequea duplicados sobre esa combinación específica en vez de la fila completa.
    """
    if columnas_clave:
        cantidad = df.duplicated(subset=columnas_clave).sum()
    else:
        cantidad = df.duplicated().sum()
    return int(cantidad)


def chequeo_completitud_temporal(
    df: pd.DataFrame,
    columna_periodo: str,
    frecuencia: str = "MS",
) -> list[str]:
    """
    Compara los períodos presentes en el dataset contra el rango completo
    esperado (ej. todos los meses entre el primero y el último dato).
    Devuelve la lista de períodos faltantes (huecos).

    Parámetros:
        columna_periodo: nombre de la columna con fechas (debe ser parseable a datetime).
        frecuencia: 'MS' para mensual (Month Start), 'W' para semanal.
    """
    fechas = pd.to_datetime(df[columna_periodo], errors="coerce")
    fechas_validas = fechas.dropna()

    if fechas_validas.empty:
        print("No se pudieron interpretar fechas en esa columna.")
        return []

    rango_completo = pd.date_range(
        start=fechas_validas.min(), end=fechas_validas.max(), freq=frecuencia
    )
    presentes = set(fechas_validas.dt.to_period("M" if frecuencia == "MS" else "W"))
    esperados = set(rango_completo.to_period("M" if frecuencia == "MS" else "W"))

    faltantes = sorted(esperados - presentes)
    return [str(p) for p in faltantes]


def chequeo_consistencia_totales(
    df: pd.DataFrame,
    columna_valor: str,
    columna_grupo: str,
    total_esperado_por_periodo: dict | None = None,
) -> None:
    """
    Suma los valores por grupo (ej. por provincia) y opcionalmente los compara
    contra un total nacional conocido, como chequeo de sanidad (sanity check).
    Sirve para detectar si el dataset tiene datos truncados o mal filtrados.
    """
    totales = df.groupby(columna_grupo)[columna_valor].sum()
    print("\nTotales por grupo:")
    print(totales)

    if total_esperado_por_periodo:
        for periodo, total_esperado in total_esperado_por_periodo.items():
            diferencia = totales.sum() - total_esperado
            print(f"\nPeríodo {periodo}: diferencia vs. total esperado = {diferencia}")


def generar_reporte_completitud(path: str | Path, columna_periodo: str | None = None) -> None:
    """Corre todos los chequeos y muestra un reporte consolidado en consola."""
    df = cargar_dataset(path)

    resumen_estructura(df)

    print("\n" + "=" * 60)
    print("VALORES FALTANTES POR COLUMNA")
    print("=" * 60)
    print(chequeo_valores_faltantes(df).to_string(index=False))

    print("\n" + "=" * 60)
    print("DUPLICADOS")
    print("=" * 60)
    print(f"Filas duplicadas (fila completa): {chequeo_duplicados(df)}")

    if columna_periodo and columna_periodo in df.columns:
        print("\n" + "=" * 60)
        print("COMPLETITUD TEMPORAL")
        print("=" * 60)
        huecos = chequeo_completitud_temporal(df, columna_periodo)
        if huecos:
            print(f"Períodos faltantes ({len(huecos)}): {huecos}")
        else:
            print("No se detectaron huecos en la serie temporal.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/data_quality.py <ruta_al_archivo> [columna_periodo]")
        sys.exit(1)

    ruta = sys.argv[1]
    col_periodo = sys.argv[2] if len(sys.argv) > 2 else None
    generar_reporte_completitud(ruta, col_periodo)
