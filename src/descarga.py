"""
descarga.py

Descarga archivos de fuentes oficiales (INDEC u otras) y los guarda en data/raw/,
sin modificarlos. Pensado para que cualquiera pueda re-correr la descarga cuando
INDEC publique una actualización, sin tener que buscar el link a mano cada vez.

Uso desde la terminal:
    python src/descarga.py <url> [nombre_archivo_destino]

Uso desde Python:
    from src.descarga import descargar_archivo
    descargar_archivo(
        "https://www.indec.gob.ar/ftp/cuadros/economia/opex_anexo_cuadros_03_09_25.xls",
        "opex_2025_semestre1.xls",
    )
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests

CARPETA_RAW = Path(__file__).resolve().parents[1] / "data" / "raw"

# Content-Type esperado según la extensión del archivo destino.
# Si el servidor devuelve otra cosa (típicamente text/html), es señal de que
# no llegamos al archivo real sino a una página de error o de redirección
# "silenciosa" (status 200 pero contenido equivocado).
TIPOS_ESPERADOS = {
    ".xls": ("application/vnd.ms-excel", "application/octet-stream"),
    ".xlsx": ("application/vnd.openxmlformats", "application/octet-stream"),
    ".csv": ("text/csv", "text/plain", "application/csv", "application/octet-stream"),
}

TAMANO_MINIMO_BYTES = 1024  # 1 KB — un archivo real de INDEC nunca es más chico que esto


class DescargaInvalida(Exception):
    """Se lanza cuando la respuesta no parece ser el archivo esperado."""


def _validar_respuesta(respuesta: requests.Response, destino: Path) -> None:
    """
    Chequea que la respuesta HTTP sea realmente el archivo esperado y no,
    por ejemplo, una página HTML de error disfrazada de 200 OK.
    """
    content_type = respuesta.headers.get("Content-Type", "").lower()
    extension = destino.suffix.lower()

    tipos_esperados = TIPOS_ESPERADOS.get(extension)
    if tipos_esperados and not any(t in content_type for t in tipos_esperados):
        raise DescargaInvalida(
            f"Se esperaba un archivo {extension} pero el servidor devolvió "
            f"Content-Type='{content_type}'. Probablemente la URL está mal "
            f"(redirección a una página HTML en vez del archivo). "
            f"Revisá el link a mano en el navegador antes de reintentar."
        )

    if len(respuesta.content) < TAMANO_MINIMO_BYTES:
        raise DescargaInvalida(
            f"El archivo descargado pesa solo {len(respuesta.content)} bytes, "
            f"demasiado poco para ser un dataset real. Probablemente la URL "
            f"no apunta al archivo correcto."
        )


def descargar_archivo(url: str, nombre_destino: str | None = None) -> Path:
    """
    Descarga un archivo desde una URL y lo guarda en data/raw/.

    Parámetros:
        url: URL directa al archivo (xls, xlsx, csv).
        nombre_destino: nombre con el que se guarda. Si no se especifica,
            se usa el nombre original del archivo tomado de la URL.

    Devuelve:
        La ruta (Path) del archivo guardado.

    Lanza:
        DescargaInvalida si la respuesta no parece ser el archivo esperado
        (ej. HTML en vez de Excel, o un archivo sospechosamente chico).
        requests.RequestException si falla la conexión, timeout, etc.
    """
    CARPETA_RAW.mkdir(parents=True, exist_ok=True)

    if nombre_destino is None:
        nombre_destino = url.split("/")[-1].split("?")[0]
    destino = CARPETA_RAW / nombre_destino

    print(f"Descargando {url} ...")
    try:
        respuesta = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        respuesta.raise_for_status()
    except requests.RequestException as error:
        raise requests.RequestException(
            f"No se pudo descargar {url}: {error}"
        ) from error

    _validar_respuesta(respuesta, destino)

    destino.write_bytes(respuesta.content)
    print(f"Guardado en: {destino} ({len(respuesta.content) / 1024:.1f} KB)")
    return destino


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/descarga.py <url> [nombre_archivo_destino]")
        sys.exit(1)

    url_arg = sys.argv[1]
    nombre_arg = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        descargar_archivo(url_arg, nombre_arg)
    except (DescargaInvalida, requests.RequestException) as error:
        print(f"ERROR: {error}")
        sys.exit(1)
