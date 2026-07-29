# Fuentes de datos — qué buscar y para qué

## 1. INDEC — dos sistemas distintos, no confundir (ver hallazgo más abajo)
- **Buscar:** dentro de `comex.indec.gob.ar`, el archivo `Serie_Opex_Mensual_AAAA_AAAA.xlsx`
  (serie mensual, todas las provincias) — **esta es la fuente principal del proyecto**.
  No usar el archivo `Datos_Origen_AAAA...xlsx` del mismo sistema como fuente
  principal: mide algo distinto (ver hallazgo metodológico).
- **Para qué:** serie temporal principal, Chaco, 2002-2026, mensual.
- **Objetivo:** #1 (evolución), #2 (estacionalidad) y #4 (composición por rubro).
- **Validado:** contra la hoja `Region-país 2015-2025 semestre` del informe
  técnico OPEX — coincide exactamente para 2021-2025. Ver `docs/inventario_datasets.md`.

## 2. Bolsa de Comercio de Rosario (BCR)
- **Buscar:** informes semanales de embarques desde el Gran Rosario, por origen si está disponible.
- **Para qué:** pulso semanal y estacionalidad real del puerto.
- **Objetivo:** #2 (estacionalidad / continuidad de campaña).

## 3. Ministerio de Economía — Economías Regionales
- **Buscar:** informes de complejos exportadores (algodón, legumbres, girasol, etc.).
- **Para qué:** decidir en qué producto conviene enfocarse según cobertura de dato.
- **Objetivo:** refinar el objetivo #1.

## 4. Bolsa de Cereales de Buenos Aires
- **Buscar:** avance de cosecha (%) y rindes por zona NEA/Chaco.
- **Para qué:** contexto de producción física, respalda la proyección.
- **Objetivo:** soporte del objetivo #4.

## 5. BCRA — ITCRM (Índice de Tipo de Cambio Real Multilateral)
- **Buscar:** serie ITCRM en el sitio del BCRA, descarga directa en Excel.
- **Para qué:** aislar el efecto del tipo de cambio real sobre el precio
  implícito de Chaco (¿la caída 2022-2024 fue por precio internacional o por
  apreciación cambiaria?).
- **Objetivo:** #4 (causas del descenso/recuperación), punto 4.5.
- **Nota técnica:** viene en frecuencia diaria — promediar a mensual
  (`resample('MS').mean()`) antes de unir con la serie de Chaco.
- **Estado:** pendiente de descargar.

## 6. Datos propios (papá / logística)
- **Buscar:** camiones despachados por mes (2023-2026), meses con/sin actividad.
- **Para qué:** dato exclusivo, valida los datos agregados oficiales "en la calle".
- **Objetivo:** #3 (cruce con logística) — es el diferencial del proyecto.

## ⚠️ Hallazgo importante: dos metodologías distintas para "origen provincial"

Existen dos fuentes del INDEC que miden algo parecido pero NO igual:

1. **Sistema `comex.indec.gob.ar` → archivo `Datos_Origen_AAAA...xls`**: asigna la
   provincia según criterio administrativo/aduanero (ej. dónde está registrado
   el exportador). Para Chaco 2024 dio un total de USD 402 millones.
2. **Informe técnico OPEX → `opex_anexo_cuadros_...xls`** (fuente oficial elegida
   para este proyecto): usa una metodología que reasigna el origen a donde se
   produjo realmente el bien. Para Chaco 2024: USD 216 millones.

**Decisión del proyecto:** se usa el informe técnico OPEX como fuente principal
para la serie de evolución de Chaco, porque refleja el origen real de la
producción (lo que el proyecto busca medir), no la ubicación administrativa
del exportador. El archivo de `comex.indec.gob.ar` se conserva como fuente
complementaria para el detalle por producto y país de destino.

## Decisión final sobre fuentes adicionales (además de INDEC)

Tras revisar Ministerio de Economía, Bolsa de Cereales de Buenos Aires, BCR y
CAME/Coninagro, la decisión es:

- **NO se necesitan fuentes adicionales para los objetivos 1, 2 y 3** — la
  serie mensual de INDEC (`Serie_Opex_Mensual_2002_2026.xlsx`) es suficiente.
- **SÍ se suman 2 fuentes puntuales para el objetivo #4** (causas), con
  extracción manual de cifras (mismo tratamiento que BCR, no son CSV para
  fusionar con la serie principal):
  1. **CAME — Monitor de Exportaciones de Economías Regionales (MEER):**
     da % de crecimiento por complejo específico (algodón, forestal, yerba
     mate) que la serie de INDEC no distingue (solo tiene "Rubro" genérico).
     Dato clave: el complejo algodonero creció 144% en 2024, pero cayó 12%
     en 2025 y sigue en crisis a mediados de 2026 (fuente: Coninagro).
  2. **Coninagro — Semáforo de Economías Regionales:** indicador cualitativo
     mensual (verde/amarillo/rojo) por actividad, útil como respaldo
     narrativo de la situación del algodón en el período analizado.
  - Contexto adicional: Chaco concentra ~45% del área algodonera nacional,
    pero dejó de ser la principal provincia productora (ese lugar lo ocupa
    ahora Santiago del Estero) — dato relevante para explicar la composición
    cambiante de las exportaciones de Chaco.
- **Bolsa de Cereales de Buenos Aires:** descartada como fuente adicional —
  se enfoca en granos (soja/maíz/trigo) a nivel nacional/pampeano, donde
  Chaco tiene peso menor; no aporta valor específico que CAME/Coninagro
  ya no den mejor para las economías regionales del NEA.

## Registro de avance por fuente

El detalle de cobertura, estructura y validación de cada archivo ya descargado
se lleva en `docs/inventario_datasets.md` (se actualiza por archivo, no acá,
para no duplicar información en dos lugares).