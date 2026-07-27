"""
explorar_excel.py

Los Excel del INDEC suelen tener varias hojas, filas de título antes del
encabezado real, celdas combinadas, etc. Este módulo sirve para MIRAR antes
de filtrar a ciegas: lista las hojas disponibles y busca en qué fila/columna
aparece un texto (por ejemplo "Chaco" o "Provincia"), para saber exactamente
dónde está la tabla real dentro del archivo.

Uso desde la terminal:
    python src/explorar_excel.py data/raw/opex_2025_semestre1.xls
    python src/explorar_excel.py data/raw/opex_2025_semestre1.xls --buscar Chaco
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def listar_hojas(path: str | Path) -> list[str]:
    """Devuelve los nombres de todas las hojas del archivo Excel."""
    xls = pd.ExcelFile(path)
    return xls.sheet_names


def resumen_hojas(path: str | Path) -> None:
    """Imprime, para cada hoja, sus dimensiones y las primeras filas crudas."""
    hojas = listar_hojas(path)
    print(f"El archivo tiene {len(hojas)} hoja(s): {hojas}\n")

    for hoja in hojas:
        # header=None: leemos todo tal cual viene, sin asumir dónde está
        # el encabezado real, porque en los archivos de INDEC casi nunca
        # es la primera fila.
        df = pd.read_excel(path, sheet_name=hoja, header=None)
        print("=" * 60)
        print(f"Hoja: {hoja} — {df.shape[0]} filas x {df.shape[1]} columnas")
        print("=" * 60)
        print(df.head(8).to_string())
        print()


def buscar_texto_en_archivo(path: str | Path, texto: str) -> list[tuple[str, int, int, str]]:
    """
    Busca un texto (ej. 'Chaco') en todas las celdas de todas las hojas.
    Devuelve una lista de coincidencias: (hoja, fila, columna, valor_celda).

    Esto sirve para ubicar exactamente dónde está la fila/columna de Chaco
    antes de armar el filtro definitivo, en vez de adivinar.
    """
    coincidencias = []
    for hoja in listar_hojas(path):
        df = pd.read_excel(path, sheet_name=hoja, header=None)
        for fila in range(df.shape[0]):
            for col in range(df.shape[1]):
                valor = df.iat[fila, col]
                if isinstance(valor, str) and texto.lower() in valor.lower():
                    coincidencias.append((hoja, fila, col, valor))

    if coincidencias:
        print(f"Se encontraron {len(coincidencias)} coincidencias de '{texto}':")
        for hoja, fila, col, valor in coincidencias:
            print(f"  Hoja='{hoja}' | fila={fila} | columna={col} | valor='{valor}'")
    else:
        print(f"No se encontró '{texto}' en ninguna hoja. Revisá mayúsculas/tildes.")

    return coincidencias


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/explorar_excel.py <ruta_archivo> [--buscar TEXTO]")
        sys.exit(1)

    ruta = sys.argv[1]

    if "--buscar" in sys.argv:
        idx = sys.argv.index("--buscar")
        texto_buscado = sys.argv[idx + 1]
        buscar_texto_en_archivo(ruta, texto_buscado)
    else:
        resumen_hojas(ruta)
