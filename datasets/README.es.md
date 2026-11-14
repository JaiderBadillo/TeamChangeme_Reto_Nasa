# Datos de Flame in Freefall

## Archivos y alcance

Para importar los datos están disponibles [nasa_master.csv](nasa_master.csv) y [nasa_synchronized.csv](nasa_synchronized.csv). Ambos usan UTF-8, coma como separador y encabezados en la primera fila. Configura el importador para interpretar los campos vacíos sin comillas como `NULL`. El CSV sincronizado exporta la tabla `measurements` de DuckDB.

| Archivo | Cobertura | Uso |
|---|---:|---|
| [nasa_master.parquet](nasa_master.parquet) | 420.421 filas, 145 columnas | Consultar las fuentes integradas, condiciones y calibraciones. |
| [nasa_synchronized.duckdb](nasa_synchronized.duckdb) | 226.124 filas únicas en `measurements` | Alimentar las gráficas del aplicativo. Incluye catálogo, condiciones y unidades. |

La entrega usa encabezados y nombres de tablas en inglés y en formato `snake_case`. Los valores, identificadores y textos originales de procedencia conservan su significado. Ambas bases se exportaron desde el maestro integrado v0.3 y la versión unificada v2.0. La carpeta contiene datos y sus dos guías, sin incorporar los archivos audiovisuales ni la documentación descargada durante la investigación.

## Selección y fuentes

Se seleccionaron cinco investigaciones de los enlaces del DOCX provisto. SAFFIRE aporta tablas calibradas y telemetría; BASS aporta condiciones de ensayo y calibración. La selección se basó en la cobertura tabular, las unidades disponibles y la posibilidad de relacionar mediciones con ensayos. El DOI y la versión identifican las fuentes consultadas.

| Investigación | NASA PSI | DOI | Versión |
|---|---|---|---:|
| SAFFIRE-I | [PSI-98](https://psi.nasa.gov/physci/repo/data/investigations/PSI-98) | 10.60555/0t15-1z43 | 4 |
| SAFFIRE-II | [PSI-99](https://psi.nasa.gov/physci/repo/data/investigations/PSI-99) | 10.60555/2chp-m469 | 5 |
| SAFFIRE-III | [PSI-100](https://psi.nasa.gov/physci/repo/data/investigations/PSI-100) | 10.60555/040q-4h36 | 4 |
| BASS | [PSI-26](https://psi.nasa.gov/physci/repo/data/investigations/PSI-26) | 10.60555/58h4-dy80 | 4 |
| BASS-II | [PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) | 10.60555/4qc4-de67 | 4 |

## Ingesta, reestructuración y limpieza

1. **Inventario y descarga.** Se consultaron las fichas PSI y el inventario público, y se descargaron directamente los CSV experimentales. Después se seleccionaron Excel y CSV de sensores, telemetría, matrices y calibración. Los manifiestos de `data/raw` y `data/expanded_raw` registran nombre, versión, DOI, tamaño y hash SHA-256.
2. **Lectura y clasificación.** El lector CSV respetó las comillas. Calamine leyó hojas Excel con pandas y el XML de los Excel originales sirvió para contrastar los recuentos. De 272 filas en los CSV experimentales, 263 se clasificaron como registros de ensayo y 9 como notas, material auxiliar o mantenimiento. Se conservaron los valores originales, las unidades publicadas y las referencias a archivo, hoja y fila.
3. **Esquema y reglas.** Se definieron tablas de ensayos, observaciones y procedencia, con mapeos por fuente. Las conversiones físicas se aplicaron a unidades explícitas y compatibles. Se distinguieron mediciones exactas, aproximadas, intervalos, límites, ausencias y sobreescala. Los identificadores, sufijos, secuencias operativas y datos ambiguos conservaron su contexto. Los ceros se trataron según el canal y el formato de la fuente, sin imputación general.
4. **Maestro de apoyo.** Sus 420.421 filas incluyen 419.558 eventos temporales, 307 registros canónicos de condiciones y 556 puntos de calibración. Se colapsaron 1.761.852 repeticiones exactas a nivel de valor, manteniendo su procedencia en el área de trabajo. Las versiones de un valor en conflicto conservan su detalle en el área de integración y aparecen como nulos en la celda correspondiente del maestro plano. El campo `missing_clock` identifica 89.942 eventos sin reloj utilizable para esa integración. La antigua vista de 330.479 filas exigía reloj presente, un criterio menos estricto que la sincronización.

## Sincronización y tabla final

Las 225.300 filas calibradas proceden de 13 ensayos. Se comprobó que el tiempo relativo fuera creciente y único por ensayo, y concordara con el epoch publicado. Para la vista sincronizada se seleccionaron 29 canales calibrados con unidades verificables. Se enmascararon 15.945 lecturas negativas del campo de rapidez del ventilador. Se conservaron los negativos de otros canales cuando la convención de signo o el cero instrumental podían explicarlos. La escala de voltaje del encendedor requiere revisión y ese canal no forma parte de la vista final.

Se evaluaron los pares de relojes Cygnus–SAFFIRE con datos reservados y se probaron correcciones por tramos. La fuente de 1 Hz de SAFFIRE-III aportó 846 filas Cygnus dentro de las ventanas de S1 y S2. Se exigió ancla exacta o dos anclas separadas como máximo 2 s. El máximo residual observado en los 427 pares reservados fue 3 ms. Los ceros de actualización ambigua en la telemetría se dejaron como nulos. Esta validación corresponde al eje temporal y los retardos físicos de los sensores siguen sin verificarse. Las demás fuentes Cygnus quedaron fuera de la publicación por desfases no resueltos o falta de cobertura dentro de los ensayos.

La unión exacta por `(experiment_id, epoch_ms)` fusionó 22 coincidencias. **225.300 + 846 − 22 = 226.124 filas únicas**, sin remuestreo ni imputación. El eje `time_s` comienza en el primer registro calibrado de cada ensayo. Los nulos se muestran como huecos. Las fichas de BASS y BASS-II aportan 735 observaciones de condiciones fuera de la tabla temporal.

## Herramientas y bibliotecas

| Herramienta | Función |
|---|---|
| Python 3.12, `urllib.request`, `csv`, `hashlib`, `zipfile` | Acceso al servicio público, lectura, hashes y empaquetado. |
| pandas y NumPy | Estructuras tabulares, limpieza, controles y análisis de relojes. |
| python-calamine y openpyxl | Lectura de Excel e inspección de hojas de origen. |
| Pint, Pydantic, Pandera | Unidades, estructura de valores y validación de tablas. |
| DuckDB y PyArrow | Integración SQL, controles de unicidad y exportación Parquet. |
| unittest, Hypothesis y lxml | Pruebas de parsers, relaciones y contraste con XML original. |
| Navegador, pypdf y lxml | Inspección del portal y extracción de contexto documental durante la investigación. |

Las versiones fijadas están en [requirements.txt](../requirements.txt). El contexto documental ayudó a interpretar las fuentes. Las mediciones sincronizadas se obtuvieron de las tablas de sensores y telemetría. PowerShell se usó para ejecutar los scripts en un entorno virtual aislado.

## Reproducción y uso

Desde la raíz del proyecto, con las fuentes descargadas, la secuencia es `build_dataset` → `build_expanded_dataset` → `integrate_all_data` → `finalize_integrated` → `clean_synchronized` → `synchronize_telemetry` → `prepare_app_data` → `release_app_data` → `release_unified_app` → `export_datasets_folder`. Los módulos se ejecutan con `python -m src.<nombre>`. Para volver a obtener las fuentes, los scripts de entrada son `download_sources`, `inventory_sources` y `download_expanded`. La auditoría de desfases está en `audit_clock_segments`.

Abrir DuckDB en modo de solo lectura. `experiment_catalog` contiene 263 registros de ensayo. La clave de `measurements` es `(experiment_id, epoch_ms)`. Consultar las unidades en `saffire_channel_units` y `cygnus_channel_units`. Se verificaron los recuentos, la unicidad, la equivalencia de los valores exportados y la consulta por ventana.

```sql
SELECT time_s, o2, co2, cygnus_pcm_air_temperature_c
FROM measurement_series('PSI-100:S1:r2', 0, 60);
```

[English documentation](README.en.md)
