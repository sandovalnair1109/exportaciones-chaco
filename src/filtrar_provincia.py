"""
filtrar_provincia.py

Una vez que con explorar_excel.py ya sabés en qué hoja y en qué fila empieza
la tabla real (el encabezado), esta función arma el filtro final: carga solo
esa hoja, salta las filas de título, y devuelve únicamente las filas que
correspondan a la provincia que te interesa.

Uso:
    from src.filtrar_provincia import filtrar_por_provincia

    df_chaco = filtrar_por_provincia(
        path="data/raw/opex_2025_semestre1.xls",
        hoja="Cuadro 7",          # nombre de hoja, obtenido con explorar_excel.py
        fila_encabezado=4,        # fila donde está el encabezado real (0-indexado)
        columna_provincia="Provincia",  # nombre de columna una vez cargado con header correcto
        provincia="Chaco",
    )
    df_chaco.to_csv("data/processed/chaco_opex.csv", index=False)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def filtrar_por_provincia(
    path: str | Path,
    hoja: str | int,
    fila_encabezado: int,
    columna_provincia: str,
    provincia: str = "Chaco",
) -> pd.DataFrame:
    """
    Carga una hoja de Excel saltando las filas de título, y filtra solo
    las filas donde columna_provincia coincida (sin distinguir mayúsculas
    ni espacios extra) con el nombre de provincia buscado.
    """
    df = pd.read_excel(path, sheet_name=hoja, header=fila_encabezado)

    # Normalizamos nombres de columnas (a veces vienen con espacios extra
    # o saltos de línea, típico de los Excel de INDEC).
    df.columns = [str(c).strip() for c in df.columns]

    if columna_provincia not in df.columns:
        raise ValueError(
            f"La columna '{columna_provincia}' no está en el archivo. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    # Normalizamos la columna de texto para comparar sin problemas de
    # mayúsculas/espacios (ej. " Chaco " vs "Chaco").
    mascara = (
        df[columna_provincia]
        .astype(str)
        .str.strip()
        .str.lower()
        == provincia.strip().lower()
    )

    resultado = df[mascara].copy()

    if resultado.empty:
        valores_unicos = df[columna_provincia].dropna().unique()
        print(
            f"No se encontraron filas para '{provincia}'. "
            f"Valores disponibles en esa columna: {list(valores_unicos)[:20]}"
        )

    return resultado


def guardar_filtrado(df: pd.DataFrame, nombre_salida: str) -> Path:
    """Guarda el resultado filtrado en data/processed/."""
    carpeta = Path(__file__).resolve().parents[1] / "data" / "processed"
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / nombre_salida
    df.to_csv(destino, index=False)
    print(f"Guardado en: {destino}")
    return destino
