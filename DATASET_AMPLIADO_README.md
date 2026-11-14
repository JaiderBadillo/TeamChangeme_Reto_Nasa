# SAFFIRE y BASS: datos ampliados — versión 0.2

Obtención y procesamiento: 14 de noviembre de 2026. Esta entrega amplía la versión de 263 registros de ensayos con archivos de sensores, telemetría, matrices, calibración y documentación de los cinco repositorios.

## Dataset principal para trabajar

`data/expanded_processed/dataset_sensores_unificado.parquet` contiene **225.300 registros temporales y 83 columnas**, incluidas las columnas de procedencia. Una fila representa una muestra temporal de un archivo de sensores calibrados, con múltiples canales. No se generaron filas artificiales, no se interpolaron datos ni se remuestrearon las señales.

También se entrega `dataset_sensores_unificado.csv.gz`. Se puede leer directamente con pandas:

```python
import pandas as pd
df = pd.read_parquet('data/expanded_processed/dataset_sensores_unificado.parquet')
# Alternativa:
df = pd.read_csv('data/expanded_processed/dataset_sensores_unificado.csv.gz')
```

| Investigación | Archivos calibrados | Registros temporales |
|---|---:|---:|
| SAFFIRE-I | 2 | 40.000 |
| SAFFIRE-II | 9 | 159.543 |
| SAFFIRE-III | 2 | 25.757 |
| Total | 13 | 225.300 |

El dataset grande procede de SAFFIRE. BASS y BASS-II aportan matrices de ensayos, condiciones, documentación y calibración. No se fabricaron series temporales para BASS a partir de su tabla de resumen.

Los canales incluyen O₂, CO₂, velocidad del aire, presión, humedad, radiometría, temperaturas de muestra y pluma, corriente/voltaje del encendedor, velocidad del ventilador y controles del equipo. Los encabezados y unidades originales están en `sensor_dictionary.csv`; no todas las 83 columnas son sensores.

La frecuencia temporal es aproximadamente 30 Hz en los archivos calibrados, con diferencias que deben consultarse en `sampling_intervals.csv`. Los datos no están limitados exclusivamente al intervalo de llama: incluyen fases de preparación y posteriores al ensayo. No se asignó una etiqueta binaria de incendio por suposición.

## Qué se recuperó

Se inventariaron los archivos públicos de PSI-98, PSI-99, PSI-100, PSI-26 y PSI-25. Se seleccionaron 110 archivos numéricos o documentos, excluyendo colecciones audiovisuales y hojas de contacto de imágenes. Se recuperaron y verificaron **105 archivos**, por un total de **484.179.099 bytes**. Cinco entradas de documentos complementarios devolvieron 404 por identificador y por nombre.

El manifiesto `data/expanded_raw/manifest.json` relaciona cada archivo con su nombre original, ruta local, versión, tamaño, DOI y hash SHA-256. Los archivos reutilizados de la primera descarga conservan su ubicación en `data/raw` o `data/telemetry_raw`; el paquete completo incluye esas rutas.

La extracción generó 97 entradas de catálogo de hojas/tablas y exclusiones de hojas de cámara. Las tablas extraídas suman 1.861.410 filas de origen, **incluidos encabezados y vistas superpuestas**. Esa cifra no equivale a observaciones independientes y no se utiliza como tamaño del dataset principal.

Los TXT comprimidos de BASS resultaron ser metadatos de fotografías (identificador, cámara, exposición, etc.). Se conservan y clasifican como tales en `archive_inventory.json`. No se contaron como lecturas de sensores ni se descargaron sus imágenes asociadas. Los libros `MergeResult` también se identifican como índices de imágenes, no sensores físicos.

## Estructura de la entrega

- `data/expanded_processed/dataset_sensores_unificado.parquet`: dataset principal, formato recomendado.
- `data/expanded_processed/dataset_sensores_unificado.csv.gz`: mismo dataset en CSV comprimido.
- `data/expanded_processed/nasa_expanded.duckdb`: tabla principal y relación con el catálogo de ensayos.
- `data/expanded_processed/counts_by_test.csv`: número de registros por ensayo.
- `data/expanded_processed/sensor_dictionary.csv`: encabezado original, unidad, columna normalizada, archivo y hoja.
- `data/expanded_processed/channel_quality.csv`: valores ausentes, ceros, mínimos y máximos por columna numérica.
- `data/expanded_processed/sampling_intervals.csv`: intervalos temporales por fuente/ensayo.
- `data/expanded_processed/validation_report.json`: controles ejecutados y archivos inaccesibles.
- `data/expanded_processed/table_catalog.csv`: ubicación y dimensiones de las tablas adicionales de las cinco investigaciones.
- `data/expanded_processed/tables/`: extracciones rectangulares completas en Parquet, con columnas posicionales `c001`, etc., para no perder encabezados repetidos o vacíos. Esas tablas requieren interpretación por fuente antes de análisis conjunto.
- `data/expanded_processed/documents/`: texto extraído de documentación y archivos TXT. Los originales conservan figuras y formato. La extracción textual no equivale a revisión científica completa.
- `data/inventory/files.json`: inventario de los cinco repositorios.
- `data/expanded_raw/excluded_inventory.json`: archivos que no se descargaron y razón de exclusión. Los ZIP no clasificados no se abrieron para buscar posibles datos internos.
- `data/processed/`: catálogo de 263 registros de ensayos y observaciones de la versión 0.1.
- `src/` y `tests/`: scripts de obtención, procesamiento, validación y pruebas.

## Limpieza y trazabilidad

Los archivos originales no se sobrescriben. Para el dataset principal se utiliza únicamente la hoja `Calibrated Data` de cada archivo de muestra: fila 1 para nombres, fila 2 para unidades y filas siguientes con tiempo numérico para observaciones.

Se normalizan nombres de columnas, preservando signos de alimentación eléctrica: por ejemplo, `PC104 -12V` y `PC104 +12V` tienen columnas diferentes. Las columnas sin encabezado se mantienen en las extracciones originales y no se publican como sensores identificados. Las unidades físicas se mantienen como las publica la fuente y se consultan por archivo en el diccionario; no se corrigen radiometrías o temperaturas por inferencia.

Cada fila tiene `record_id`, `investigation_id`, `source_test_id`, `source_file_id`, `source_file_name`, `source_sheet` y `source_row`. El tiempo relativo se expresa en `elapsed_time_s`. `epoch_time` y `timestamp_ms` conservan las representaciones de origen; no se debe suponer que cualquier columna temporal de las tablas auxiliares usa segundos solo por su nombre.

La unión con el catálogo utiliza investigación e identificador de ensayo. En DuckDB, la vista `sensors_with_experiment` añade material, dirección de flujo e identificador del experimento, sin multiplicar filas.

No se concatenaron todas las hojas de telemetría como si fueran datos independientes: existen versiones raw, procesadas, submuestras y resúmenes del mismo fenómeno. Las fuentes adicionales se conservan por separado. Los datos generales de telemetría contienen valores iniciales anómalos y ceros potencialmente ligados a actualización de canales; no se imputaron ni interpretaron automáticamente como mediciones físicas válidas.

## Verificación realizada

- 225.300 identificadores únicos.
- Tiempos relativos y tiempos epoch sin duplicados dentro de cada archivo calibrado.
- Tiempo relativo estrictamente creciente por archivo.
- Todos los registros principales enlazan con uno de los 13 ensayos de SAFFIRE del catálogo.
- La unión no añade ni elimina registros.
- Esquema tabular comprobado con Pandera.
- Tamaño y hash de los 105 archivos recuperados verificados.
- Sin errores de extracción registrados.

Estos controles son estructurales. La calibración es la reportada por NASA, no una recalibración independiente. Una gran cantidad de instantes no sustituye una gran cantidad de ensayos independientes. Para modelos, separar entrenamiento y evaluación por ensayo/campaña para evitar fuga de información entre instantes cercanos. La selección de variables y las etiquetas de incendio requieren una tarea predictiva definida.

## Archivos que siguieron inaccesibles

- PSI-98: `SAFFIRE Offgassing Testing Strategy.pdf`.
- PSI-100: `SAFFIRE Offgassing Testing Strategy.pdf`.
- PSI-100: presentaciones de las conferencias 45, 46 y 47 listadas en el manifiesto.

No falló la descarga de los 13 archivos principales de sensores calibrados. Los 404 corresponden a documentación complementaria. El contenido audiovisual continúa excluido.

## Reproducir

Con Python 3.12 y `requirements.txt`:

```powershell
python src/inventory_sources.py          # Red: inventario público
python src/download_expanded.py         # Red: datos y documentos seleccionados
python src/build_expanded_dataset.py    # Local: extracción y consolidación
python src/validate_expanded.py         # Local: controles
python -m unittest discover -s tests -v
```

La actualización de fuentes debe ejecutarse sobre una copia si se desea conservar esta instantánea. El manifiesto registra los errores pendientes. El script de descarga general reutiliza archivos existentes; las fuentes nuevas deben mantener sus hashes y versiones.

## Atribución

Citar los DOI originales almacenados en los manifiestos por investigación, junto con la versión y fecha de consulta. La unificación es una transformación local de datos públicos de NASA PSI; no una nueva publicación oficial de NASA.
