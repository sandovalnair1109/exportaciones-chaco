"""
Fase 4.8.a — Generar data/raw/retenciones_chaco.csv de forma reproducible
Fuente: docs/cronologia_retenciones.md (transcripción manual de los 6 decretos,
        ya verificados contra texto oficial InfoLeg/BORA donde se indica)

Por qué existe este script y no se edita el CSV a mano:
- Si aparece un séptimo decreto o se corrige un valor, el cambio se hace acá
  (en REGISTROS) y se vuelve a correr el script — no se edita el CSV
  directamente. Editar el CSV a mano rompe la trazabilidad: la próxima vez
  que alguien corra este script, pisaría la corrección manual sin darse cuenta.
- Permite validaciones automáticas (fechas bien formadas, fin > inicio,
  sin filas duplicadas, sin solapamientos) antes de guardar, algo que no
  se puede hacer tecleando directamente en una terminal.

Uso desde notebook:
    %run ../src/fase4_generar_retenciones_csv.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "data" / "raw" / "retenciones_chaco.csv"

# ─── REGISTROS ────────────────────────────────────────────────────────────
# Una fila por (ventana temporal, producto). Transcripción manual desde
# docs/cronologia_retenciones.md — ver ese archivo para el detalle de cada
# decreto y su nivel de confirmación contra fuente oficial.
#
# confianza:
#   "alta"  = fecha, mecanismo Y valor de alícuota confirmados en texto oficial
#   "media" = fecha y mecanismo confirmados en texto oficial, valor por prensa
#   "baja"  = incluido en el decreto según prensa, valor puntual no confirmado
REGISTROS = [
    {"fecha_inicio": "2025-01-27", "fecha_fin": None,         "producto": "algodon",    "alicuota_pct": 0.0,  "decreto": "38/2025",  "confianza": "media", "nota": "Anexo I generico 0% confirmado en texto oficial - que algodon este en Anexo I es segun prensa (Anexo no visto)"},
    {"fecha_inicio": "2025-01-27", "fecha_fin": "2025-06-30", "producto": "soja",       "alicuota_pct": 26.0, "decreto": "38/2025",  "confianza": "media", "nota": "Anexo II, mecanismo y fecha confirmados oficialmente, valor por prensa"},
    {"fecha_inicio": "2025-01-27", "fecha_fin": "2025-06-30", "producto": "trigo",      "alicuota_pct": 9.5,  "decreto": "38/2025",  "confianza": "media", "nota": "Anexo II, mecanismo y fecha confirmados oficialmente, valor por prensa"},
    {"fecha_inicio": "2025-01-27", "fecha_fin": "2025-06-30", "producto": "maiz_sorgo", "alicuota_pct": None, "decreto": "38/2025",  "confianza": "baja",  "nota": "incluido en Anexo II segun prensa, valor puntual no confirmado"},
    {"fecha_inicio": "2025-07-01", "fecha_fin": "2025-09-22", "producto": "trigo",      "alicuota_pct": 9.5,  "decreto": "439/2025", "confianza": "media", "nota": "prorroga confirmada en texto oficial (mecanismo), tasa igual a la de 38/2025 — partida en dos filas (misma logica que soja/maiz_sorgo) para dejar hueco a la ventana 0% de 682/2025"},
    {"fecha_inicio": "2025-09-26", "fecha_fin": "2025-12-11", "producto": "trigo",      "alicuota_pct": 9.5,  "decreto": "439/2025", "confianza": "media", "nota": "continuacion de 439/2025 tras la ventana 0% de 682/2025, hasta ser reemplazada por 877/2025 (corregido: fecha_fin original de esta prorroga era 2026-03-31, lo cual solapaba con 877/2025)"},
    {"fecha_inicio": "2025-07-01", "fecha_fin": "2025-07-31", "producto": "soja",       "alicuota_pct": 33.0, "decreto": "439/2025", "confianza": "media", "nota": "reversion implicita por no estar en el Anexo de prorroga (mecanismo confirmado, valor por prensa)"},
    {"fecha_inicio": "2025-07-01", "fecha_fin": "2025-07-31", "producto": "maiz_sorgo", "alicuota_pct": 12.0, "decreto": "439/2025", "confianza": "media", "nota": "reversion implicita, valor por prensa"},
    {"fecha_inicio": "2025-08-01", "fecha_fin": "2025-09-22", "producto": "soja",       "alicuota_pct": 26.0, "decreto": "526/2025", "confianza": "media", "nota": "reduccion permanente, mecanismo confirmado, valor por prensa"},
    {"fecha_inicio": "2025-08-01", "fecha_fin": "2025-09-22", "producto": "maiz_sorgo", "alicuota_pct": 9.3,  "decreto": "526/2025", "confianza": "media", "nota": "reduccion permanente, mecanismo confirmado, valor por prensa"},
    {"fecha_inicio": "2025-09-23", "fecha_fin": "2025-09-25", "producto": "soja",       "alicuota_pct": 0.0,  "decreto": "682/2025", "confianza": "alta",  "nota": "0% total confirmado en texto oficial, ventana de 3 dias confirmada por agotamiento de cupo (prensa)"},
    {"fecha_inicio": "2025-09-23", "fecha_fin": "2025-09-25", "producto": "maiz_sorgo", "alicuota_pct": 0.0,  "decreto": "682/2025", "confianza": "alta",  "nota": "idem soja"},
    {"fecha_inicio": "2025-09-23", "fecha_fin": "2025-09-25", "producto": "trigo",      "alicuota_pct": 0.0,  "decreto": "682/2025", "confianza": "alta",  "nota": "idem soja"},
    {"fecha_inicio": "2025-09-26", "fecha_fin": "2025-12-11", "producto": "soja",       "alicuota_pct": 26.0, "decreto": "526/2025", "confianza": "media", "nota": "vuelve la alicuota de 526/2025 al vencer la ventana del 682/2025"},
    {"fecha_inicio": "2025-09-26", "fecha_fin": "2025-12-11", "producto": "maiz_sorgo", "alicuota_pct": 9.3,  "decreto": "526/2025", "confianza": "media", "nota": "idem soja"},
    {"fecha_inicio": "2025-12-12", "fecha_fin": "2026-06-03", "producto": "soja",       "alicuota_pct": 24.0, "decreto": "877/2025", "confianza": "media", "nota": "reduccion permanente, mecanismo/fecha confirmados oficialmente, valor por prensa"},
    {"fecha_inicio": "2025-12-12", "fecha_fin": "2026-06-03", "producto": "trigo",      "alicuota_pct": 7.5,  "decreto": "877/2025", "confianza": "media", "nota": "idem soja"},
    {"fecha_inicio": "2025-12-12", "fecha_fin": "2026-06-03", "producto": "maiz_sorgo", "alicuota_pct": 8.5,  "decreto": "877/2025", "confianza": "media", "nota": "idem soja"},
    {"fecha_inicio": "2026-06-04", "fecha_fin": None,         "producto": "trigo",      "alicuota_pct": 5.5,  "decreto": "423/2026", "confianza": "media", "nota": "cronograma inmediato (Anexo I cultivos invierno), mecanismo/fecha confirmados oficialmente"},
    {"fecha_inicio": "2026-06-04", "fecha_fin": None,         "producto": "soja",       "alicuota_pct": 24.0, "decreto": "423/2026", "confianza": "media", "nota": "se mantiene en 2026 dentro del cronograma gradual (Anexo II), baja recien desde dic. 2027"},
]


def validar_sin_solapamientos(df: pd.DataFrame) -> None:
    """
    Verifica que, para un mismo producto, no haya dos ventanas temporales
    vigentes al mismo tiempo. A diferencia del chequeo de duplicados (que
    solo detecta fecha_inicio idéntica), esto agarra el caso de dos filas
    con fecha_inicio DISTINTA cuyos rangos igual se superponen — el tipo de
    error que puede quedar cuando se agrega un decreto nuevo y no se acorta
    la fecha_fin del decreto que reemplaza.
    """
    for producto, grupo in df.groupby("producto"):
        grupo = grupo.sort_values("fecha_inicio_dt")
        fin_anterior = None
        inicio_anterior = None
        for _, fila in grupo.iterrows():
            if fin_anterior is not None and fila["fecha_inicio_dt"] <= fin_anterior:
                raise ValueError(
                    f"Solapamiento de fechas en producto '{producto}': la ventana que "
                    f"empieza {fila['fecha_inicio']} (decreto {fila['decreto']}) se "
                    f"superpone con la ventana anterior, que termina "
                    f"{fin_anterior.date() if fin_anterior is not pd.Timestamp.max else 'vigente'} "
                    f"(decreto correspondiente a esa fila anterior, inicio {inicio_anterior})."
                )
            fin_anterior = fila["fecha_fin_dt"] if pd.notna(fila["fecha_fin_dt"]) else pd.Timestamp.max
            inicio_anterior = fila["fecha_inicio"]


def construir_dataframe() -> pd.DataFrame:
    """Arma el DataFrame a partir de REGISTROS y valida su consistencia."""
    df = pd.DataFrame(REGISTROS)

    df["fecha_inicio_dt"] = pd.to_datetime(df["fecha_inicio"])
    df["fecha_fin_dt"] = pd.to_datetime(df["fecha_fin"])

    # Validación 1: donde hay fecha_fin, tiene que ser posterior a fecha_inicio.
    con_fin = df.dropna(subset=["fecha_fin_dt"])
    invertidas = con_fin[con_fin["fecha_fin_dt"] < con_fin["fecha_inicio_dt"]]
    if not invertidas.empty:
        raise ValueError(f"Filas con fecha_fin anterior a fecha_inicio:\n{invertidas}")

    # Validación 2: no debería haber dos filas idénticas en (producto, fecha_inicio).
    duplicadas = df.duplicated(subset=["producto", "fecha_inicio"])
    if duplicadas.any():
        raise ValueError(f"Filas duplicadas en (producto, fecha_inicio):\n{df[duplicadas]}")

    # Validación 3 (nueva): dos ventanas del mismo producto no pueden solaparse,
    # aunque tengan fecha_inicio distinta (ver docstring de validar_sin_solapamientos).
    validar_sin_solapamientos(df)

    return df.drop(columns=["fecha_inicio_dt", "fecha_fin_dt"])


def generar_csv() -> Path:
    """Construye, valida y guarda el CSV en data/raw/."""
    df = construir_dataframe()
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DESTINO, sep=";", index=False)
    return DESTINO


if __name__ == "__main__":
    destino = generar_csv()
    df = pd.read_csv(destino, sep=";")
    print(f"CSV generado y validado: {destino}")
    print(f"Filas: {len(df)} | Decretos distintos: {df['decreto'].nunique()}")
    print(f"Confianza: {df['confianza'].value_counts().to_dict()}")