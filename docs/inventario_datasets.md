# Inventario de datasets — data/raw/

Este documento registra qué es cada archivo bajado, su estructura, y para qué
sirve en el proyecto. Se actualiza a mano cada vez que se agrega un archivo nuevo.

## Serie_Opex_Mensual_2002_2026.xlsx ⭐ FUENTE PRINCIPAL

- **Origen:** Sistema de Consulta de Comercio Exterior (comex.indec.gob.ar),
  incluido en el zip mensual de exportaciones.
- **Cobertura:** 2002 a junio 2026, mensual, TODAS las provincias.
- **Columnas:** Año, Mes, FOB_dólar, Peso neto (kg), Nombre Prov, Nombre_Región, Rubro.
- **Validado:** los totales anuales coinciden exactamente con el informe oficial
  OPEX (misma metodología de asignación de origen real de producción).
- **Para qué sirve:** serie temporal principal de Chaco — objetivos 1 y 2.
- **Limitación:** no tiene detalle de producto específico ni país de destino,
  solo "Rubro" (PP/MOA/MOI/CyE).

## opex_anexo_cuadros_10_03_26.xls

- **Origen:** Informe técnico "Origen provincial de las exportaciones. Bienes.
  Año 2025" (INDEC).
- **Cobertura:** Totales anuales 2022-2025, por provincia y por complejo exportador.
- **Para qué sirve:** cifra "de referencia" para citar en conclusiones (ej. "según
  INDEC, Chaco exportó USD 235M en 2025"). También sirvió para VALIDAR que
  Serie_Opex_Mensual usa la misma metodología.
- **Limitación:** son tablas ya resumidas, no hay con qué construir un análisis
  propio más allá de lo que el cuadro ya muestra.

## Datos_origen_2024_mayo_2025.xlsx

- **Origen:** Sistema de Consulta de Comercio Exterior, modalidad anual, archivo
  específico de origen provincial.
- **Cobertura:** Solo año 2024. Por provincia, producto (DESCRIP_RUBRO) y país
  de destino (DESCRIP_PAIS), en USD y kg.
- **Para qué sirve:** ver QUÉ exporta Chaco y A QUIÉN, con detalle fino — pero
  solo para 2024.
- **⚠️ Limitación importante:** usa una metodología de asignación de provincia
  DISTINTA a Serie_Opex_Mensual / OPEX oficial (da 402M para Chaco 2024 en vez
  de 216M). NO mezclar sus totales con los de la fuente principal.

## prod_soja_acum_2002_2025.xlsx / prod_soja_mens_2002_2023.xlsx

- **Origen:** Sistema de Consulta de Comercio Exterior.
- **Cobertura:** Complejo soja, NACIONAL (sin desglose por provincia), 2002-2025.
- **Para qué sirve:** contexto nacional (ej. si el precio internacional de la
  soja cayó, eso explicaría parte de la caída de Chaco en USD aunque el volumen
  físico se mantenga). NO tiene a Chaco desglosado.

## exponm26.csv / expopm26.csv / etotnm26.csv / etotpm26.csv (y sus versiones anuales _a_)

- **Origen:** Sistema de Consulta de Comercio Exterior, bases generales.
- **Cobertura:** Exportaciones NACIONALES por producto (NCM) y país de destino.
  `etot...` son solo totales de control (2 filas), no datos para analizar.
- **Para qué sirve:** contexto nacional de a qué países se vende y qué productos
  crecen/caen a nivel país. NO tienen Chaco desglosado.

## Explicativo_base_anual_OPEX.docx / Leame_exportaciones.docx

- Documentación metodológica del INDEC, no son datos.

## data/processed/chaco_serie_mensual_2002_2026.csv ⭐ DATASET DE TRABAJO (Fase 1 en adelante)

- **Origen:** resultado de aplicar `filtrar_provincia.py` sobre `Serie_Opex_Mensual_2002_2026.xlsx`.
- **Cobertura:** 2002 a junio 2026, mensual, solo Chaco. 884 filas, sin nulos, sin duplicados.
- **Columnas:** Año, Mes, FOB_dólar, Peso neto, Nombre Prov, Nombre_Región, Rubro.
- **Validado:**
  - Estructura y completitud: `src/validar_dataset_procesado.py` (notebook `paso5_validacion_dataset_procesado.ipynb`).
  - Coincidencia exacta con la serie oficial de primer semestre de INDEC
    (hoja `Region-país 2015-2025 semestre` del anexo OPEX), para los 5 años
    donde ambas series se solapan (2021-2025) — validación cruzada, no solo
    interna.
- **A partir de este archivo se construye todo el análisis de las Fases 1 a 4.**
  No se vuelve a tocar `Serie_Opex_Mensual_2002_2026.xlsx` directamente salvo
  para volver a filtrar si hiciera falta otra provincia de comparación.

## Nota sobre data_quality.py y su wrapper

`data_quality.py` es una **librería genérica** de funciones de chequeo
(nulos, duplicados, huecos temporales) — no está pensada para correrse sola
con `%run` desde un notebook (espera un argumento de línea de comandos).
Para Chaco específicamente, se usa a través de dos wrappers que sí siguen el
patrón del proyecto (ruta hardcodeada, `%run` sin argumentos):

- `src/chequeo_calidad_chaco.py` (Fase 1.2) — nulos, duplicados por clave
  `Año/Mes/Rubro`, y huecos temporales (arma una columna de fecha temporal
  en memoria, ya que el CSV trae `Año`/`Mes` separados).
- `src/validar_dataset_procesado.py` (Fase 0.9.bis) — validación estructural
  del archivo procesado (filas esperadas, columnas, provincia única).