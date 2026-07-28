# Exportaciones de Chaco — Análisis de tendencia 2022-2026

## Objetivo general

Analizar la evolución de las exportaciones agroindustriales de Chaco (2022–2026)
para identificar si el primer semestre de 2026 representa una recuperación
fuerte de la actividad exportadora y logística hacia los puertos de Rosario,
tras la caída registrada entre 2022 y 2025.

> **Nota sobre el ajuste del objetivo:** el planteo original suponía un "récord
> histórico" continuo. Los datos oficiales (ver hallazgos abajo) muestran una
> caída sostenida 2022→2024 y una fuerte recuperación en el primer semestre de
> 2026 respecto a 2023-2025 — pero todavía por debajo del pico de 2022. El
> objetivo se ajustó para reflejar lo que los datos muestran, no lo supuesto
> al inicio.

## Objetivos específicos

1. Cuantificar la evolución mensual de exportaciones de Chaco, en valor (USD)
   y en volumen (toneladas), 2022-2026.
2. Comparar la intensidad de "campaña" (estacionalidad) entre años — ver si
   2026 muestra menos pausa entre campañas que años anteriores.
3. Relacionar volumen exportado con actividad logística (datos agregados
   propios, a conseguir).
4. Investigar las posibles causas del descenso 2022-2024 y de la recuperación
   2026 (precios internacionales vs. volumen físico, composición de productos).

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

## Fuente de datos principal — CONFIRMADA

**`Serie_Opex_Mensual_2002_2026.xlsx`** (Sistema de Consulta de Comercio
Exterior, INDEC): serie mensual 2002-2026, con provincia, región, rubro,
valor FOB en USD y peso neto en kg. Se validó que usa la misma metodología
que el informe técnico oficial OPEX (los totales anuales coinciden
exactamente). Es la fuente principal para los objetivos 1 y 2.

## ⚠️ Hallazgos importantes hasta ahora

1. **Dos metodologías distintas de "origen provincial" en el INDEC:**
   - `comex.indec.gob.ar` → archivo `Datos_Origen_AAAA...xls`: asigna
     provincia por criterio administrativo/aduanero. Chaco 2024 = USD 402M.
   - Informe técnico OPEX (y `Serie_Opex_Mensual`): reasigna al origen real
     de producción. Chaco 2024 = USD 216M. **Esta es la fuente elegida.**

2. **La serie real de Chaco no es un crecimiento continuo:**

   | Año | Exportaciones (millones USD) |
   |---|---|
   | 2022 | 517 |
   | 2023 | 304 |
   | 2024 | 216 |
   | 2025 | 235 |

3. **Primer semestre, comparado año a año (USD y toneladas):**

   | Año | USD (millones) | Toneladas |
   |---|---|---|
   | 2022 | 220,6 | 613.887 |
   | 2023 | 132,9 | 335.094 |
   | 2024 | 111,8 | 251.189 |
   | 2025 | 101,9 | 239.549 |
   | **2026** | **152,0** | **341.259** |

   2026 muestra una recuperación fuerte (+49% en USD, +42% en toneladas
   vs. 2025), pero todavía por debajo del pico de 2022.

4. **Archivos que son solo contexto nacional (NO tienen Chaco desglosado):**
   `exponm/expopm` (por NCM/país), `prod_soja_mens/acum` (complejo soja
   nacional), bases anuales `expona25/expopa25`. Sirven de contexto, no
   para el análisis provincial.

Ver `docs/fuentes.md` para el detalle completo de cada fuente.

## Flujo para descargar y filtrar datos de una fuente nueva (ej. INDEC)

1. **Descargar el archivo** (queda en `data/raw/`, sin modificar):
   ```bash
   python src/descarga.py <url_del_archivo> nombre_deseado.xls
   ```

2. **Explorar la estructura** (los archivos de INDEC tienen títulos y encabezados
   corridos, no asumas que la fila 0 es el encabezado real):
   ```bash
   python src/explorar_excel.py data/raw/nombre_deseado.xls
   python src/explorar_excel.py data/raw/nombre_deseado.xls --buscar Chaco
   ```
   Esto te dice en qué hoja, fila y columna aparece lo que buscás.

   ⚠️ Solo funciona con archivos Excel (`.xls`/`.xlsx`). Los `.csv` del
   sistema de comercio exterior (separados por `;`, codificación latin1)
   todavía no tienen un lector propio en este repo.

3. **Filtrar la provincia** una vez que sabés hoja/fila de encabezado:
   ```python
   from src.filtrar_provincia import filtrar_por_provincia, guardar_filtrado

   df_chaco = filtrar_por_provincia(
       path="data/raw/nombre_deseado.xls",
       hoja="Cuadro X",
       fila_encabezado=4,
       columna_provincia="Provincia",
       provincia="Chaco",
   )
   guardar_filtrado(df_chaco, "chaco_2025.csv")
   ```
   ⚠️ Solo tiene sentido si el archivo tiene una columna de provincia. Los
   archivos nacionales (por NCM/país) no la tienen y este script no aplica.

4. **Chequear completitud** del resultado filtrado (ver sección siguiente).

## Cómo correr el chequeo de completitud de datos

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/data_quality.py data/raw/indec_exportaciones_chaco.csv
```
