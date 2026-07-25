# Exportaciones del Norte Argentino — Análisis Chaco

Análisis de la evolución de las exportaciones agroindustriales del Chaco (2023–2026),
con foco en determinar si el primer semestre de 2026 representa un pico histórico
de producción y actividad logística hacia los puertos de Rosario.

## Objetivo general

Analizar la evolución de las exportaciones agroindustriales del norte del Chaco
(2023–2026) para identificar si el primer semestre de 2026 representa un pico
histórico de producción y actividad logística hacia los puertos de Rosario.

## Objetivos específicos

1. Cuantificar la evolución mensual/trimestral de volúmenes exportados por Chaco.
2. Comparar la intensidad de "campaña" (estacionalidad) entre años.
3. Relacionar volumen exportado con actividad logística (datos agregados propios).
4. Proyectar/estimar (sin precisión oficial) el cierre 2026 en base a la tendencia
   del primer semestre.

## Estructura del repositorio

```
exportaciones-chaco/
├── data/
│   ├── raw/            # Datos originales, sin modificar (INDEC, BCR, etc.)
│   └── processed/      # Datos limpios, listos para análisis
├── notebooks/          # Exploración y análisis (Jupyter)
├── src/                # Código reutilizable (carga, limpieza, validación)
├── docs/               # Documentación del proyecto, fuentes, decisiones
└── tests/              # Pruebas de las funciones de src/
```

## Fuentes de datos

| Fuente | Cobertura | Estado |
|---|---|---|
| INDEC — Intercambio Comercial Argentino (ICA) | Provincial, mensual | En progreso |
| Bolsa de Comercio de Rosario (BCR) | Embarques Gran Rosario, semanal | Pendiente |
| Ministerio de Economía — Economías Regionales | Por complejo exportador | Pendiente |
| Bolsa de Cereales de Buenos Aires | Avance de cosecha | Pendiente |
| Datos propios (logística familiar) | Camiones/mes, agregado | Pendiente |

Ver `docs/fuentes.md` para el detalle de qué buscar en cada una.

## Cómo correr el chequeo de completitud de datos

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/data_quality.py data/raw/indec_exportaciones_chaco.csv
```
