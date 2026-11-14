# Datos integrados de SAFFIRE y BASS, versión 0.3

Esta entrega contiene datos tabulares, sin informes, presentaciones, manuales, documentos gráficos ni índices de imágenes. Es una integración local de fuentes originales de NASA PSI; no una publicación oficial de NASA.

## Archivos para trabajar

- `data/integrated/dataset_analisis.parquet`: vista recomendada de 330.479 registros. Excluye eventos sin reloj presente, pero conserva las condiciones planificadas/reportadas y la calibración como tipos distintos. No implica validación científica de cada canal.
- `data/integrated/dataset_analisis.csv.gz`: misma vista en CSV comprimido.
- `data/integrated/dataset_integrado.parquet`: maestro completo de 420.421 registros y 145 columnas, con indicadores de calidad. También disponible como CSV comprimido.
- `data/integrated/sensores_calibrados_completos.parquet`: las 225.300 filas y todas las columnas de los sensores calibrados de la entrega anterior, incluidas señales operativas auxiliares.
- `data/integrated/observations.parquet`: 11.628.452 versiones distintas de valores por canal e instante, después de consolidar coincidencias exactas. Son lecturas de canales, no 11,6 millones de ensayos o instantes independientes.
- `data/integrated/measurement_lineage.parquet`: 13.390.304 referencias a celdas originales; conserva todas las procedencias, incluidas las de valores repetidos.
- `data/integrated/matrix_records.parquet`: 428 registros de matrices con origen; `matrix_fields.parquet` contiene campos interpretados. Las coincidencias exactas se consolidan en 307 registros canónicos dentro de la base de datos.
- `data/integrated/calibration_records.parquet`: 556 puntos de calibración por bloque, preservando encabezados de fecha/GMT y etiquetas originales.
- `data/integrated/nasa_integrado.duckdb`: base relacional completa y vistas de consulta.
- `source_tables.csv`, `channel_dictionary.csv`, `counts_by_record_type.csv` y `report.json`: procedencia, variables, recuentos y verificación.

## Qué significa una fila

El maestro usa `record_type` para distinguir **eventos temporales**, **condiciones reportadas**, **condiciones planificadas**, **condiciones sin medios asociados** y **puntos de calibración**. No calcular estadísticas mezclando esos tipos. Los 420.421 registros se componen de 419.558 eventos temporales, 307 registros canónicos de condiciones y 556 puntos de calibración.

Cada evento temporal corresponde a investigación, dominio de procesamiento, reloj e instante. Los dominios `sample_calibrated` y `telemetry` se mantienen separados: representan procesamientos diferentes y pueden describir el mismo fenómeno. Los relojes de Cygnus y SAFFIRE tampoco se alinean automáticamente ni se convierten a un único origen UTC.

De los eventos temporales, 89.942 carecen de reloj numérico positivo en la fuente. Se preservan con identidad de origen, se marcan mediante `missing_clock` y se excluyen de `dataset_analisis`. El reloj presente no garantiza sincronización, fecha correcta o ausencia de reinicios.

## Qué se añadió

Se incorporaron RawData, CygnusData, SaffireData, las tablas de presión, temperatura y humo, y los CSV de telemetría de SAFFIRE. También se integraron matrices de BASS, matrices de BASS-II y la calibración del ventilador. La correspondencia entre matrices y ensayos debe verificarse con sus identificadores y condiciones; los registros planificados no demuestran ejecución.

Se descartaron de esta entrega los índices MergeResult y los metadatos fotográficos TXT. Los valores ficticios para dibujar líneas en gráficos de presión se excluyeron. Las filas de introducción y notas operativas ajenas a los datos en matrices tampoco se incluyeron. Los originales permanecen en las entregas previas del espacio de trabajo, pero no forman parte de los nuevos ZIP de datos.

## Repeticiones, conflictos y unidades

Se consolidaron 1.761.852 repeticiones exactas de valores con igual investigación, dominio, reloj, instante, ensayo, canal, unidad y valor. No se redondeó para hacer coincidir valores. Las relaciones de procedencia se conservaron completas.

Cuando el mismo contexto/canal/unidad presenta valores distintos, todas las versiones permanecen en `observations`, con `has_conflicting_values=true`. En el maestro plano la celda correspondiente queda nula: no se elige una versión arbitrariamente ni se calcula un promedio. Los nombres ambiguos no se consideran equivalentes por similitud textual.

Las columnas de señal en el maestro incluyen dominio, canal y unidad publicada, o `unit_unspecified` si la tabla no declara una unidad. No comparar esas columnas como si todas estuvieran calibradas o fueran dimensionalmente equivalentes. Los valores de matrices conservan su texto original: una cabecera de O₂ rotulada como porcentaje con valores tipo fracción no se corrige sin evidencia adicional.

La vista de análisis aún puede contener otras limitaciones de instrumentación y correlación temporal. Para modelos, dividir por ensayo o campaña, no aleatoriamente entre instantes vecinos. No se crearon etiquetas de incendio ni se inventaron mediciones.

## Reproducibilidad

Con las fuentes y extracciones de versiones previas presentes:

```powershell
python -m src.integrate_all_data
python -m src.finalize_integrated
python -m unittest discover -s tests -v
```

El paquete de detalle permite trabajar con Parquet sin cargar en memoria todas las lecturas. Por ejemplo, DuckDB puede consultar `observations.parquet` directamente. Los DOI, nombres originales y hashes están en el catálogo de fuentes. La base DuckDB conserva además el catálogo original de 263 registros y sus observaciones.
