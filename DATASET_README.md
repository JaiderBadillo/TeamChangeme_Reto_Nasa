# Dataset unificado de combustión NASA PSI — versión 0.1.0

Se obtuvieron directamente los cinco CSV experimentales originales de NASA PSI el 14 de noviembre de 2026. No se descargaron videos, imágenes ni las colecciones completas de los repositorios. El pipeline preserva todas las celdas de las tablas descargadas y no imputa observaciones.

## Archivos principales

- `data/processed/dataset_unificado.csv`: vista plana con un registro por fila experimental original, útil para inspección e integración inicial.
- `data/processed/nasa_unified.duckdb`: base relacional con ensayos, observaciones, protocolos, notas, recursos, registros originales y advertencias.
- `data/processed/experiments.json`: ensayos en JSON para consumo desde un backend o prototipo web.
- `data/processed/observations.parquet` y `.json`: observaciones y metadatos por celda, con unidades y calificadores.
- `data/processed/sources.json`: URL, DOI, versión, fecha de descarga, archivo y SHA-256 de las fuentes.
- `data/processed/data_dictionary.csv`: columnas, tipos y cobertura no nula de las tablas exportadas.
- `data/staging/column_mappings.json`: equivalencias explícitas de encabezados.
- `data/quality/quality_issues.csv`: cola de revisión por ensayo y campo.
- `data/quality/report.json`: conciliación de registros y métricas del proceso.
- `data/raw/`: cinco CSV originales y respuestas públicas de metadatos sin alterar.

Las tablas relacionadas se entregan en CSV, JSON y Parquet. El CSV plano es una vista de conveniencia; los intervalos, límites, notas y calificadores completos están en `observations` y las tablas relacionadas. No utilizar el CSV plano como sustituto de esas semánticas.

## Cobertura

| Investigación | Fuente | Filas originales | Registros experimentales | Otras filas |
|---|---|---:|---:|---:|
| SAFFIRE-I | PSI-98 | 4 | 2 | 2 auxiliares |
| SAFFIRE-II | PSI-99 | 15 | 9 | 2 auxiliares y 4 notas |
| SAFFIRE-III | PSI-100 | 2 | 2 | 0 |
| BASS | PSI-26 | 122 | 121 | 1 mantenimiento |
| BASS-II | PSI-25 | 129 | 129 | 0 |
| Total | | 272 | 263 | 9 |

El portal mostraba una fila vacía adicional al final de cada tabla. Esa fila no existe como registro en los CSV originales descargados. Los 263 registros no deben interpretarse como 263 muestras independientes: hay reutilización de muestras y variantes de prueba.

## Estructura y reglas

`experiment_id` identifica un registro experimental y combina investigación, identificador publicado y posición en el CSV. Es único en esta instantánea; un cambio de orden en una fuente futura requiere reconciliar identidades. `source_record_id` apunta a la fila original. `csv_record_number` cuenta registros CSV lógicos empezando por el encabezado como 1; no es necesariamente una línea física del archivo.

`source_records` conserva encabezados y valores originales como arrays JSON. `observations` contiene una fila por celda experimental, incluidos metadatos y ausencias: sus 3.116 filas no son 3.116 mediciones numéricas.

Campos de una observación:

| Campo | Significado |
|---|---|
| `raw_value` | Texto original sin sobrescribir |
| `source_column` | Encabezado original |
| `field` | Nombre canónico |
| `status` | numeric, approximate, interval, bound, missing, not_applicable, overrange, qualitative, ambiguous o text |
| `value` | Valor numérico escalar cuando existe |
| `lower_bound`, `upper_bound` | Límites o extremos de un intervalo |
| `unit` | Unidad del valor normalizado, si está determinada |
| `qualifier` | Aproximación, operador o cambio ordenado |
| `method` | Lectura reportada, dato derivado o metadato |
| `usable_for_analysis` | Cumple el parsing y no tiene una advertencia bloqueante en esta versión; no certifica validez científica |
| `quality_flags` | Array JSON de incidencias |

Las unidades de longitud se convierten a mm mediante Pint cuando la unidad original es explícita. La velocidad se conserva en cm/s o mm/s según magnitud. Oxígeno y CO₂ se expresan como porcentaje de volumen, no como fracción 0–1; CO se conserva en ppm. Los porcentajes solo se convierten entre representaciones equivalentes; no se infiere composición molar/masa.

Un `>500` no se transforma en 500 exactos. Un intervalo no se convierte en su media. `22.1 to 22.0` conserva el calificador de cambio ordenado y el texto original; no se interpreta como intervalo de incertidumbre. `Insignificant` no equivale a cero segundos. `none`, celda vacía y `n/a` se conservan en el texto original y en estados diferenciados cuando corresponde.

Los valores no disponibles en una tabla no se completan con los de otra investigación. No hay forward fill de materiales ni equivalencias difusas automáticas. Los nombres explícitos se normalizan, manteniendo descripción original y texto de grado de Nomex. Las barras descritas solo como `clear rod` no se etiquetan automáticamente PMMA.

`condition_protocols` conserva las secuencias originales de aire, ventilador y ganancia de BASS-II. No se reconstruyeron etapas temporales porque las tablas no proporcionan los instantes de cambio ni una correspondencia inequívoca entre listas. `resources` conserva identificadores de cámara como referencias, sin descargar audiovisuales ni inventar URLs.

Las notas de SAFFIRE-II se relacionan como contexto de tabla. La columna `scope` aclara que su aplicabilidad específica debe verificarse con las referencias de cada celda; no se afirma que cada nota aplique íntegramente a cada ensayo.

## Calidad y límites

Se identificaron 161 advertencias (no necesariamente 161 ensayos distintos):

- 95 materiales no resueltos porque faltan o no son explícitos.
- 18 campos con semántica no confirmada en encabezados `?-g`.
- 13 lecturas negativas de CO.
- 8 discrepancias entre fecha y código GMT/día.
- 5 lecturas de O₂ fuera del intervalo conservador de revisión de esta campaña (10–25 %), no un umbral general de seguridad.
- Otras 22 advertencias sobre dimensiones, unidades, componentes, fechas y textos numéricos ambiguos.

El valor numérico interpretado de una celda sospechosa se conserva en `observations`; queda con `usable_for_analysis=false` y no se publica como escalar utilizable en la vista plana. Por ejemplo, se mantienen O₂ final de 1,6 %, 39,1 % y 40,4 % con advertencias. Estos valores no se corrigieron por inferencia.

Los espesores de SIBAL de SAFFIRE-I/III se marcan para contraste documental; las dimensiones longitud/anchura de SAFFIRE-I también presentan un conflicto con la descripción. El encabezado `?-g Spread Length` de SAFFIRE-II no se reemplaza por velocidad confirmada aunque haya valores en mm/s.

La vista DuckDB `observations_analysis` filtra el indicador de uso, pero incluye intervalos y límites que requieren tratamiento específico. Para una gráfica o promedio de escalares hay que filtrar además `status IN ('numeric','approximate')`, `value IS NOT NULL`, la magnitud y unidades compatibles. Ninguna consulta debe mezclar campos físicos por compartir una unidad.

```sql
SELECT e.study_name, e.source_test_id, o.field, o.value, o.unit, o.qualifier
FROM observations_analysis o
JOIN experiments e USING (experiment_id)
WHERE o.field = 'oxygen_initial'
  AND o.status IN ('numeric', 'approximate')
  AND o.value IS NOT NULL;
```

La compilación no certifica materiales, no reconstruye curvas temporales ni valida un predictor de incendio. La revisión científica de las advertencias y el enriquecimiento con documentos adicionales siguen pendientes.

## Reproducibilidad

Bibliotecas: pandas, Pandera, Pint, Pydantic, DuckDB, PyArrow y Hypothesis. Las versiones exactas están en `requirements.txt` y `data/quality/report.json`.

Desde la raíz del proyecto, con Python 3.12 y las dependencias instaladas:

```powershell
python src/download_sources.py  # Solo para actualizar las fuentes; requiere Internet
python src/build_dataset.py     # Reconstrucción local sin Internet
python -m unittest discover -s tests -v
```

Para preservar esta instantánea, copiarla antes de ejecutar una actualización de fuentes. La descarga guarda únicamente CSV experimentales seleccionados en los metadatos públicos. No conserva URLs firmadas temporales. El hash de cada CSV permite verificar los originales.

Validación ejecutada: nueve pruebas automatizadas satisfactorias, incluidas pruebas basadas en propiedades de Hypothesis; conciliación de las 272 filas, conservación de celdas originales, unicidad de claves, relaciones entre tablas, tratamiento de ceros/ausencias/límites y exclusión analítica de valores sospechosos. Las pruebas no sustituyen la revisión científica de los datos.

## Fuentes y atribución

Cada registro conserva el DOI de su investigación y el enlace a NASA PSI. Los DOI y versiones exactos de esta descarga están en `data/processed/sources.json`. Para publicaciones, citar los datasets originales, además de describir estas transformaciones. Los CSV descargados corresponden a las investigaciones PSI-98, PSI-99, PSI-100, PSI-26 y PSI-25.
