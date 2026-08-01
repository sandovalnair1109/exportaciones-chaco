# Plan de trabajo — Exportaciones de Chaco (2002-2026)
## Fases y mini-objetivos detallados

> **Regla general que atraviesa todas las fases:** toda cifra externa (CAME,
> Coninagro, prensa) que se use en el proyecto debe registrarse con tres datos
> obligatorios: **nivel geográfico** (Chaco / NEA / Nacional), **período
> exacto** (ej. "año calendario 2024" vs. "últimos 12 meses a mayo 2026" — no
> son lo mismo y se prestan a confusión), y **URL + fecha de consulta**. Esto
> surgió porque ya nos pasó una vez: una cifra de "los últimos 12 meses" se
> comparó por error contra una de "año calendario 2025" y parecían
> contradecirse. La tabla de la Fase 0.12 (`docs/matriz_de_citas.md`) es donde
> se centraliza esto.

---

## Fase 0 — Preparación (COMPLETA)

- **0.1.** Definir objetivo general y objetivos específicos del proyecto.
- **0.2.** Armar estructura de repositorio (`data/`, `src/`, `docs/`, `tests/`, `notebooks/`).
- **0.2.bis (agregado, orden real corregido)** Crear y activar el entorno
  virtual **antes** de instalar cualquier dependencia. Hacerlo después (como
  pasó acá) desincroniza `requirements.txt` con lo que realmente está
  instalado — sin gravedad, pero es la lección operativa más simple de este
  proyecto y vale la pena dejarla escrita.
- **0.3.** Conectar el repo a GitHub.
- **0.4.** Escribir script de descarga con validación (`descarga.py`) + tests.
- **0.5.** Escribir script de exploración de Excel (`explorar_excel.py`).
- **0.6.** Escribir script de filtrado por provincia (`filtrar_provincia.py`).
- **0.7.** Identificar y descargar la fuente principal (`Serie_Opex_Mensual_2002_2026.xlsx`).
- **0.8. (detallado en pasos reales, ver `notebooks/`)** Validar metodología:
  - `analizar_microdatos_chaco_2024.py` → exploración inicial de un archivo
    candidato (`Datos_origen_2024_mayo_2025.xlsx`).
  - `verificar_totales_anuales.py` → extraer el total oficial 2022-2025 de
    `opex_anexo_cuadros_10_03_26.xls`.
  - `comparar_discrepancias_2024.py` → comparó ambos y encontró 86,2% de
    discrepancia → decisión: descartar `Datos_origen...` como fuente
    principal, usar `Serie_Opex_Mensual` (ver hallazgo en `docs/fuentes.md`).
  - `verificar_primer_semestre.py` → construyó la serie de primer semestre
    2002-2026 desde `Serie_Opex_Mensual` y la comparó contra la hoja oficial
    `Region-país 2015-2025 semestre` — coincide exactamente en 2021-2025.
- **0.9.** Filtrar Chaco de la fuente principal → `chaco_serie_mensual_2002_2026.csv` (884 filas).
- **0.9.bis (nuevo)** `validar_dataset_procesado.py` (notebook
  `validacion_dataset_procesado.ipynb`): último chequeo, esta vez sobre
  el **archivo procesado** (no la fuente) — confirma que el filtro no perdió
  ni duplicó filas, que `Nombre Prov` contiene únicamente "Chaco", y que no
  hay nulos. Reutiliza `chequeo_valores_faltantes`/`chequeo_duplicados` de
  `data_quality.py` en vez de reimplementarlos.
- **0.10.** Documentar el inventario de datasets (`docs/inventario_datasets.md`).
- **0.11.** Documentar la discrepancia metodológica entre fuentes (`docs/fuentes.md`).
- **0.12.** Crear `docs/matriz_de_citas.md`: tabla con `Cifra | Nivel geográfico
  | Período exacto | Fuente + URL | Fecha de consulta | Usada en objetivo #`.
  Cada cifra externa (no de tu propia serie filtrada) se registra ahí ANTES
  de usarse en cualquier gráfico o conclusión.
- **0.13. (nuevo, recomendado)** Guardar la reflexión "camino real vs. camino
  ideal" como `docs/leccion_aprendida_metodologia.md` — documenta que el
  orden correcto es *validar antes de adoptar una fuente*, no al revés. Útil
  para la narrativa de la PPS, no solo como nota interna.

**Secuencia real de los notebooks de validación (para referencia):**
`explorador_archivos_excel.ipynb` → `analisis_exploratorio_chaco_2024.ipynb`
→ `verificacion_datos_oficiales.ipynb` → `analisis_discrepancias_2024.ipynb`
→ `verificacion_primer_semestre.ipynb` → `validacion_dataset_procesado.ipynb`.

---

## Fase 1 — Objetivo específico #1: Cuantificar la evolución mensual (USD y toneladas)

- **1.1.** Cargar `chaco_serie_mensual_2002_2026.csv` con pandas en un notebook nuevo.
- **1.2. (corregido)** Correr `src/fase1_chequeo_calidad_chaco.py` (wrapper de
  `data_quality.py` con los parámetros correctos para Chaco — nulos,
  duplicados por clave `Año/Mes/Rubro`, y huecos temporales). Este script
  arma una columna de fecha **temporal, solo en memoria**, para poder
  chequear huecos, sin adelantar la persistencia formal del paso 1.3.
  **1.1 y 1.2 se consolidaron en un mismo notebook**
  (`notebooks/fase1_carga_y_chequeo_calidad_chaco.ipynb`), renombrado
  después de agregar el 1.1 sobre un notebook que originalmente solo
  tenía el 1.2.
- **1.3.** Crear la columna de fecha real (`Año` + `Mes` → tipo `datetime`),
  **de forma persistente esta vez** (a diferencia del 1.2) — script
  `src/fase1_agregar_columna_fecha.py`, sobreescribe directamente
  `data/processed/chaco_serie_mensual_2002_2026.csv`. Notebook:
  `notebooks/fase1_columna_fecha_chaco.ipynb`.
- **1.4.** Agrupar por fecha y sumar `FOB_dólar` y `Peso neto` → serie
  mensual total de Chaco (294 meses, sin distinguir rubro). **1.4 a 1.12
  se concentraron en un solo notebook**
  (`notebooks/fase1_serie_mensual_chaco.ipynb`), por ser pasos de una
  misma narrativa (serie → gráficos → variación → tabla anual →
  conclusión).
- **1.5.** Graficar la serie completa 2002-2026 en USD (línea de tiempo).
  Observación agregada: el pico histórico en USD está cerca de 2011, no
  de 2022 — coincide con la validación de la Fase 0.
- **1.6.** Graficar la misma serie en toneladas. Observación agregada:
  el pico histórico en toneladas está cerca de 2019, no coincide con el
  pico en USD — indicio temprano de variación en el precio implícito
  (a cuantificar en Fase 4.1).
- **1.7.** Marcar visualmente en el gráfico los años clave: 2022 (pico
  previo), 2024 (piso), 2026 (recuperación). Aclaración agregada: "pico
  previo" se refiere al período reciente 2022-2025, no al máximo
  histórico de toda la serie (ver 1.5-1.6).
- **1.8.** Calcular variación % interanual mes a mes. Hallazgo: racha de
  7 meses consecutivos (dic-2025 a jun-2026) con variación positiva en
  USD, con una excepción real en **junio 2026** (toneladas -0,4%, único
  valor negativo del tramo) — primera aparición de una anomalía que se
  repite en la Fase 2.
- **1.9.** Armar tabla resumen anual (2015-2026). Sirvió además como
  **validación cruzada**: los totales coinciden exactamente con los ya
  confirmados en la Fase 0 (517/304/216/235/152).
- **1.10. (prioritaria — hecha primero, como estaba previsto)**
  Contrastar el total anual 2025 contra el oficial — diferencia de
  -0,000%, tercera confirmación de que la cadena de procesamiento no
  introdujo errores.
- **1.11.** Columna de acumulado año a fecha (`groupby(año).cumsum()`) —
  permitió la comparación justa que reveló la recuperación real de
  2026 (+49% USD, +42% toneladas vs. el piso de 2025).
- **1.12.** Conclusión parcial redactada — con dos afirmaciones
  corregidas antes de cerrarla (una comparación contra "toda la serie
  histórica" que en realidad no era el máximo, y una generalización
  sobre "todos los meses en dos dígitos" que no aplicaba a junio en
  toneladas). Mismo criterio de verificación que se venía aplicando a
  fuentes externas, ahora sobre afirmaciones propias.

  **Fase 1 — COMPLETA.**
---

## Fase 2 — Objetivo específico #2: Estacionalidad / continuidad de campaña

- **2.1.** Para cada año, calcular qué meses tuvieron el volumen más bajo.
- **2.2.** Calcular el coeficiente de variación mensual (desvío estándar / promedio) de cada año.
- **2.3.** Comparar ese coeficiente entre 2022, 2023, 2024, 2025 y el semestre disponible de 2026.
- **2.4.** Calcular **índice de estacionalidad**: `valor_mes / promedio_anual * 100`.
  Permite frases del tipo "julio históricamente representa el 85% del promedio
  mensual, pero en 2026 representó el 130%".
- **2.5.** Graficar los 12 meses de cada año superpuestos (un color por año).
- **2.6.** Enriquecer con una **banda sombreada del rango histórico**
  (mínimo-máximo o percentiles 25-75, 2015-2025) y superponer 2026 como línea
  destacada — mucho más contundente que 12 líneas finas sin referencia.
- **2.7.** Aclarar siempre que 2026 tiene menos meses de datos disponibles
  (probablemente hasta junio/julio) al comparar contra años completos.
- **2.8.** Redactar conclusión parcial.
**Nota metodológica (agregada al cierre de la fase):** los pasos 2.2 y
2.4-2.6 se calcularon originalmente con base **anual** (12 meses), lo
cual no era comparable de forma justa contra 2026 (año parcial, 6
meses). Se agregaron los pasos 2.3 y 2.7 recalculando con base
**semestral**, permitiendo comparar los 6 años en igualdad de
condiciones. Hallazgo real: la tendencia decreciente del coeficiente de
variación 2021-2025 (años completos) es real y se sostiene, pero el
**segundo semestre de cada año tiene una dinámica propia**, distinta a
la del primero — no es una simple continuación lineal. El índice de
estacionalidad, con base corregida, mostró que 2026 se mueve dentro del
rango histórico en la mayoría de los meses, con dos excepciones reales:
marzo por encima de todo el rango 2021-2025, y junio por debajo —
confirmado que no es un problema de datos incompletos (mismo conteo de
filas/rubros que el resto de la serie).

**Fase 2 — COMPLETA.**

---

## Fase 3 — Objetivo específico #3: Cruce con logística (dato de tu papá)

- **3.1.** Pedir a tu papá: camiones despachados por mes, 2023-2026.
- **3.2.** Armar el CSV manual de BCR con 3-4 cifras puntuales de
  embarques/camiones en el Gran Rosario, con sus URLs de respaldo (registrar
  nivel geográfico: Gran Rosario/nacional, no Chaco puntual).
- **3.3.** Armar CSV propio con los datos de tu papá
  (`data/raw/logistica_propia.csv`), documentando explícitamente que es
  **"dato de campo ilustrativo, no muestra estadísticamente representativa"**.
- **3.4.** Unir (por mes) la serie de Chaco con la de BCR y, donde haya, la de tu papá.
- **3.5.** **Normalizar todas las series a índice base 100** (ej. enero 2023 =
  100) antes de graficar — USD, toneladas y camiones no son comparables en
  la misma escala cruda.
- **3.6.** Graficar las series normalizadas juntas.
- **3.7.** Aclarar en el texto la diferencia entre correlación y causalidad:
  que dos series suban juntas es consistente con la hipótesis, no una prueba
  de causalidad (podría haber una tercera causa, como el clima de la campaña).
- **3.8.** Redactar conclusión parcial.

---

## Fase 4 — Objetivo específico #4: Causas del descenso 2022-2024 y la recuperación 2026

- **4.1.** Calcular el "precio implícito" por tonelada de cada año: `FOB_dólar / Peso neto`.
- **4.2.** Graficar la evolución de ese precio implícito 2015-2026.
- **4.3.** Comparar: ¿la caída 2022→2024 se explica más por menos volumen (kg) o por menor precio (USD/kg)?
- **4.4.** (Usando `prod_soja_acum_2002_2025.xlsx`) Contrastar el precio
  implícito de Chaco contra el precio internacional de la soja.
- **4.5.** Sumar el **ITCRM** (Índice de Tipo de Cambio Real Multilateral,
  BCRA, descargable con `descarga.py`). Responde una pregunta distinta a la
  del 4.4: si el peso se apreció en términos reales 2022-2024, eso solo puede
  explicar buena parte de la caída del precio implícito en USD, más allá de
  si el precio internacional de la soja cayó o no.
  **Actualizado:** el archivo ya fue descargado (ver `docs/fuentes.md` y
  `docs/inventario_datasets.md`) — cobertura real verificada 1997 a
  julio 2026, más amplia que lo indicado en el catálogo web del BCRA.
  Falta el script de exploración de estructura (`src/explorar_itcrm.py`,
  pendiente) antes de poder cruzarlo con la serie de Chaco.
- **4.6.** Agrupar por `Rubro` (PP/MOA/MOI/CyE) y ver si cambió la composición
  de lo que exporta Chaco entre 2022 y 2026.
- **4.7.** Recién después del 4.6, incorporar el contexto externo del complejo
  algodonero (CAME/Coninagro) como **"hipótesis a contrastar"**, no como
  explicación a confirmar. Verificar cualquier cifra citada contra la fuente
  original y registrarla en `docs/matriz_de_citas.md` con nivel geográfico y
  período exacto.
- **4.8.** Evaluar la hipótesis del algodón contra los datos propios de Chaco.
  Dos resultados posibles, **ambos válidos y publicables**: (a) el Rubro
  asociado a algodón perdió peso relativo en 2025-2026 (respalda la
  hipótesis), o (b) no perdió peso pese a la crisis nacional del sector
  (hallazgo igual de interesante: "Chaco no dependía tanto del algodón como
  se suponía").
- **4.9.** Redactar conclusión: ¿la recuperación 2026 es "más de lo mismo" o cambió qué exporta Chaco?

---

## Fase 5 — Cierre y presentación

- **5.1.** Consolidar las 4 conclusiones parciales en `docs/conclusiones.md`.
- **5.2.** Revisar `docs/matriz_de_citas.md` completa: ninguna cifra externa
  sin nivel geográfico o período documentado.
- **5.3.** Decidir el formato final (notebook, reporte, o Streamlit) — recién
  acá, con todo el análisis hecho. Dado que ya tenés experiencia con Streamlit
  y este proyecto tiene una narrativa geográfica fuerte, un dashboard con
  mapa de Chaco, serie temporal interactiva y filtro por rubro sería el
  cierre más potente para el portfolio — no obligatorio si el tiempo aprieta.
- **5.4.** Revisar que todo el código tenga tests mínimos donde corresponda.
- **5.5.** Última limpieza del README, contado como historia, no como
  changelog de scripts. Estructura sugerida: (1) la pregunta que dispara el
  proyecto; (2) qué encontraste, 4-5 líneas por objetivo; (3) las 4
  conclusiones parciales consolidadas; (4) cómo correr el proyecto (lo
  técnico, al final).