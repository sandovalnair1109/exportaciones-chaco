# Matriz de citas — cifras externas usadas en el proyecto

Toda cifra que NO salga directamente de `chaco_serie_mensual_2002_2026.csv`
(nuestra fuente filtrada) se registra acá ANTES de usarse en cualquier
gráfico o conclusión, con su nivel geográfico y período exacto.

| Cifra | Nivel geográfico | Período exacto | Fuente + URL | Fecha de consulta | Usada en objetivo # |
|---|---|---|---|---|---|
| Chaco exportó USD 517M / 304M / 216M / 235M (2022-2025) | Chaco (provincia) | Año calendario 2022, 2023, 2024, 2025 | Informe técnico OPEX INDEC — opex_anexo_cuadros_10_03_26.xls | 2026-07-25 | #1 |
| Complejo algodonero nacional: +144,4% en USD, +115,1% en toneladas | **Nacional** (no Chaco) | Año calendario 2024 vs. 2023 | CAME / Infobae, nota "21 de 22 economías regionales..." | 2026-07-26 | #4 (hipótesis a contrastar, NO conclusión directa sobre Chaco) |
| Complejo algodonero: exportaciones -12%, importaciones +119% | Nacional | Reportado nov. 2025, referido a situación reciente (confirmar período exacto antes de usar) | Coninagro / noticiasagropecuarias.com | 2026-07-26 | #4 (pendiente de precisar período) |
| Algodón "en rojo" en el Semáforo de Economías Regionales | Nacional (por actividad, no por provincia) | Mayo 2026 | Coninagro / chacodiapordia.com | 2026-07-26 | #4 (contexto cualitativo) |
| Chaco concentra ~45% del área algodonera nacional, pero ya no es la mayor provincia productora (ese lugar es de Santiago del Estero) | Chaco (comparativo con otras provincias) | Sin fecha exacta en la fuente — verificar año de referencia antes de citar en el informe final | noticiasagropecuarias.com, nov. 2025 | 2026-07-26 | #4 (contexto) |
| Embarques Gran Rosario: 4,9 millones de toneladas en diciembre 2025 (3er registro más alto de la historia) | Gran Rosario (no Chaco) | Diciembre 2025 | Bolsa de Comercio de Rosario (BCR) | 2026-07-26 | #3 (contexto logístico, no dato de Chaco) |
| Exportaciones de soja julio 2025 fueron 4x julio 2024; camiones de trigo al Gran Rosario, máximo desde 2020 (sistema STOP) | Gran Rosario / Nacional | Julio 2025 | BCR | 2026-07-26 | #3 (contexto logístico) |

## Cómo agregar una fila nueva

Antes de citar cualquier cifra en un notebook o en el README:
1. Buscá la fuente original (no una nota que cite a otra nota).
2. Confirmá el nivel geográfico exacto (¿es de Chaco, del NEA, o nacional?).
3. Confirmá el período exacto (¿año calendario? ¿acumulado 12 meses? ¿un mes puntual?).
4. Agregá la fila acá ANTES de usar la cifra en el análisis.
