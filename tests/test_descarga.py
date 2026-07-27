"""Tests para src/descarga.py — corré con: pytest tests/"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.descarga import descargar_archivo, DescargaInvalida


def _respuesta_falsa(content: bytes, content_type: str, status_ok: bool = True) -> Mock:
    mock = Mock()
    mock.content = content
    mock.headers = {"Content-Type": content_type}
    mock.raise_for_status = Mock() if status_ok else Mock(side_effect=requests.HTTPError)
    return mock


@patch("src.descarga.requests.get")
def test_descarga_exitosa_guarda_archivo(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr("src.descarga.CARPETA_RAW", tmp_path)
    contenido = b"x" * 2048  # 2 KB, simula un .xls real
    mock_get.return_value = _respuesta_falsa(contenido, "application/vnd.ms-excel")
    destino = descargar_archivo("https://ejemplo.com/datos.xls")
    assert destino.exists()
    assert destino.read_bytes() == contenido


@patch("src.descarga.requests.get")
def test_html_disfrazado_de_xls_lanza_error(mock_get, tmp_path, monkeypatch):
    """
    Caso real: INDEC devuelve la home del sitio (HTML, status 200) cuando
    la URL del .xls está mal armada. No debe guardarse como si fuera válido.
    """
    monkeypatch.setattr("src.descarga.CARPETA_RAW", tmp_path)
    html_falso = b"<html><body>Pagina de inicio</body></html>" * 50
    mock_get.return_value = _respuesta_falsa(html_falso, "text/html; charset=utf-8")
    with pytest.raises(DescargaInvalida, match="Content-Type"):
        descargar_archivo("https://ejemplo.com/datos.xls")


@patch("src.descarga.requests.get")
def test_archivo_demasiado_chico_lanza_error(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr("src.descarga.CARPETA_RAW", tmp_path)
    contenido_chico = b"error"
    mock_get.return_value = _respuesta_falsa(contenido_chico, "application/vnd.ms-excel")
    with pytest.raises(DescargaInvalida, match="demasiado poco"):
        descargar_archivo("https://ejemplo.com/datos.xls")
