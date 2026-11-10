# Exportaciones de Chaco (2002-2026): ¿qué pasó y por qué?

Entre 2022 y 2024, las exportaciones de Chaco cayeron **58%** (de USD 517M a
USD 216M). En el primer semestre de 2026 se recuperaron con fuerza. Este
proyecto, hecho con datos oficiales del INDEC, intenta responder dos preguntas:

1. **¿Se recuperó Chaco de verdad en 2026?**
2. **¿Por qué cayó, y por qué volvió a subir?** La explicación más a mano es el
   precio internacional. ¿Alcanza?

## Lo que encontré

**1. La recuperación de 2026 es real, pero parcial.**
En el primer semestre de 2026 Chaco exportó USD 152,0M: +49% en dólares y +42%
en toneladas frente al primer semestre de 2025. Sigue **31% por debajo** del
primer semestre de 2022 (USD 220,6M).

| Año | Total anual (M USD) | 1.er semestre (M USD) | 1.er semestre (toneladas) |
|---|---|---|---|
| 2022 | 517 | 220,6 | 613.887 |
| 2023 | 304 | 132,9 | 335.094 |
| 2024 | 216 | 111,8 | 251.189 |
| 2025 | 235 | 101,9 | 239.549 |
| **2026** | (parcial) | **152,0** | **341.259** |

**2. Las campañas se volvieron más parejas.**
La variabilidad mensual de las exportaciones bajó (coeficiente de variación de
0,394 a 0,165 entre 2021 y 2025). En 2026, marzo (índice 111,5) quedó por encima
del rango histórico y junio (90,8) por debajo.

**3. La caída fue de volumen, no de precio, y se concentró en un tipo de producto.**
- **El volumen explica entre el 86% y el 159%** de la variación en dólares en
  los cinco tramos analizados. Supera 100% cuando el precio empujó en sentido
  contrario.
- **Productos Primarios (PP) cayó 69,5%** entre 2022 y 2024. Las manufacturas de
  origen agropecuario (MOA) crecieron 36,1%, pero compensaron apenas una
  fracción: +USD 18,7M frente a -USD 320,9M. PP pasó de 89,4% del total en 2022
  a 65,4% en 2026.
- **El precio promedio parece subir, pero es un espejismo.** Pasó de 398 a
  448 USD/ton porque cambió *qué* se exporta (más manufacturas, que valen más por
  tonelada). *Dentro* de cada rubro el precio bajó entre 8% y 10%: un aporte
  menor frente al volumen.
- **La soja no explica la magnitud** (cayó 26,7% en ese período, mucho más que el
  precio de los rubros de Chaco). **El tipo de cambio real quedó descartado**
  para 2022-2024: casi no se movió (+0,2%).
- **Retenciones:** con los datos disponibles no se pueden evaluar para la caída
  (la cronología arranca en enero de 2025) y no muestran señal clara en la
  recuperación.

**Qué NO puedo decir:** estos datos muestran *qué* se movió, no *por qué* cayó
el volumen físico de PP (clima, siembra, crisis del algodón y otras causas
quedan fuera de lo que se puede medir acá).

## Cómo llegué (el recorrido)

| Fase | Qué hice |
|---|---|
| **0. Datos** | Conseguir los archivos originales y elegir la fuente. |
| **1. Limpieza** | Cargar, chequear calidad y construir la serie mensual de Chaco. |
| **2. Movimiento por años** | Comparar años y estacionalidad. |
| **3. Logística** | Descartada: no hay datos propios de transporte. El objetivo #3 queda fuera de alcance. |
| **4. Causas** | Probar las explicaciones una por una (ver abajo). |
| **5. Cierre** | Conclusiones, revisión de citas y este README. |

**Fase 4, en orden:** precio implícito (4.1-4.2) → descomposición precio vs.
volumen (4.3) → precio de la soja (4.4) → tipo de cambio real (4.5) →
composición por rubro (4.6) → retenciones (4.8) → síntesis que cruza todo (4.9)
→ conclusión (4.10) → nota de contexto sobre el algodón (4.11).

## ⚠️ Decisiones sobre los datos

1. **El INDEC publica dos versiones de "origen provincial".**
   - `comex.indec.gob.ar` asigna la provincia por criterio administrativo o
     aduanero. Chaco 2024 = USD 402M.
   - El informe técnico OPEX (y `Serie_Opex_Mensual`) reasigna al origen real de
     producción. Chaco 2024 = USD 216M. **Es la fuente elegida.**
2. **Fuente principal:** `Serie_Opex_Mensual_2002_2026.xlsx` (INDEC), serie
   mensual con provincia, rubro, valor FOB y peso neto. Sus totales anuales
   coinciden exactamente con el informe técnico oficial.
3. **Archivos solo de contexto nacional** (sin Chaco desglosado): `exponm/expopm`,
   `prod_soja_mens/acum`, `expona25/expopa25`. Se usaron para la soja como
   referencia de precio.
4. **Alcance temporal:** los datos llegan hasta junio de 2026, así que 2026 se
   compara siempre contra el primer semestre de los otros años.

Detalle completo de cada fuente en `docs/fuentes.md`.

## Limitaciones

- La serie de Chaco distingue **rubro** (PP, MOA, MOI, CyE) pero no producto
  específico.
- El precio de la soja es un **proxy nacional** (precio implícito de exportación
  argentina), no una cotización internacional.
- La cronología de retenciones cubre desde 2025; la caída 2022-2024 queda sin
  evaluar en ese frente.
- Las cifras de algodón son nacionales, no de Chaco.

## Estructura del repositorio

```
exportaciones-chaco/
├── data/
│   ├── raw/            # Datos originales, sin modificar (INDEC, BCRA, etc.)
│   └── processed/      # Datos limpios, listos para análisis
├── notebooks/          # Análisis por fase (Jupyter), con conclusión en cada uno
├── src/                # Código reutilizable (carga, limpieza, validación, fase 4)
├── docs/               # Fuentes, conclusiones, matriz de citas, plan de trabajo
└── tests/              # Pruebas de las funciones de src/
```

## Cómo reproducirlo

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Después abrí los notebooks de `notebooks/` en orden de fase. Cada uno corre su
script de `src/` con `%run ../src/<script>.py` y termina con su conclusión.

Para chequear la calidad de un archivo de datos:

```bash
python src/data_quality.py data/raw/indec_exportaciones_chaco.csv
```

<details>
<summary>Flujo para incorporar una fuente nueva (ej. INDEC)</summary>

1. **Descargar** (queda en `data/raw/`, sin modificar):
   ```bash
   python src/descarga.py <url_del_archivo> nombre_deseado.xls
   ```
2. **Explorar la estructura.** Los archivos del INDEC tienen títulos y encabezados
   corridos, no asumas que la fila 0 es el encabezado real:
   ```bash
   python src/explorar_excel.py data/raw/nombre_deseado.xls
   python src/explorar_excel.py data/raw/nombre_deseado.xls --buscar Chaco
   ```
   Solo funciona con Excel (`.xls`/`.xlsx`). Los `.csv` del sistema de comercio
   exterior (separados por `;`, latin1) todavía no tienen lector propio.
3. **Filtrar la provincia:**
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
   Solo aplica si el archivo tiene columna de provincia.
4. **Chequear completitud** del resultado.

</details>
