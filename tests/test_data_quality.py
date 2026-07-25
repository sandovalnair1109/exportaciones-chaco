"""Tests básicos para src/data_quality.py — corré con: pytest tests/"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data_quality import (
    chequeo_valores_faltantes,
    chequeo_duplicados,
    chequeo_completitud_temporal,
)


def test_chequeo_valores_faltantes_detecta_nulos():
    df = pd.DataFrame({"provincia": ["Chaco", None], "toneladas": [100, 200]})
    reporte = chequeo_valores_faltantes(df)
    fila_provincia = reporte[reporte["columna"] == "provincia"].iloc[0]
    assert fila_provincia["faltantes"] == 1


def test_chequeo_duplicados_cuenta_bien():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [1, 1, 3]})
    assert chequeo_duplicados(df) == 1


def test_chequeo_completitud_temporal_detecta_hueco():
    df = pd.DataFrame({"periodo": ["2026-01-01", "2026-03-01"]})
    huecos = chequeo_completitud_temporal(df, "periodo")
    assert "2026-02" in huecos
