# Plan del sistema CombusLab

## Propósito

CombusLab es un proyecto para el reto **Flame in Freefall** de la hackathon **NASA Space Apps Challenge 2026**. El aplicativo web facilita la búsqueda y comparación de investigaciones sobre combustión en microgravedad y la interpretación de su relevancia para la prevención, detección y supresión de incendios en misiones espaciales.

El público incluye ingenieros de seguridad, investigadores, estudiantes y docentes. El recorrido principal parte de una pregunta de seguridad, pasa por las fichas y los ensayos pertinentes, y termina con una comparación, una explicación con citas o una descarga de los datos seleccionados.

## Alcance y cobertura de datos

| Investigación integrada | NASA PSI | Uso en el MVP |
|---|---|---|
| SAFFIRE-I y SAFFIRE-II | [PSI-98](https://psi.nasa.gov/physci/repo/data/investigations/PSI-98) y [PSI-99](https://psi.nasa.gov/physci/repo/data/investigations/PSI-99) | Fichas y series calibradas según el ensayo y canal disponibles. |
| SAFFIRE-III | [PSI-100](https://psi.nasa.gov/physci/repo/data/investigations/PSI-100) | Fichas, series calibradas y telemetría Cygnus alineada en dos ensayos. |
| BASS y BASS-II | [PSI-26](https://psi.nasa.gov/physci/repo/data/investigations/PSI-26) y [PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) | Fichas y observaciones tabulares de condiciones experimentales. El maestro conserva calibraciones y procedencia. |

El catálogo operativo, las comparaciones, el ranking y las exportaciones abarcan estos cinco estudios. SoFIE, SAME/SAME-R y FLEX/FLEX-2 son candidatos para evaluar después de la hackathon. Las referencias externas sobre detección, gotas, gravedad parcial o transferencia tecnológica pueden aportar contexto editorial con citas.

| Recurso | Estado y función |
|---|---|
| `public.nasa_synchronized` | Cargado en Supabase con 226.124 filas de 13 ensayos. Es la fuente de las gráficas y exportaciones temporales. Su clave primaria es `(experiment_id, epoch_ms)`. |
| `public.nasa_master` | Cargado en Supabase con 420.421 filas. Conserva eventos, condiciones, calibraciones y procedencia. Las relaciones con las series requieren comprobar la clave y la cardinalidad. |
| Metadatos del DuckDB local | `experiment_catalog` contiene 263 registros, `experiment_conditions` contiene 735 observaciones y los diccionarios `saffire_channel_units` y `cygnus_channel_units` contienen 377 y 11 filas, respectivamente. Su carga reproducible a Supabase se prevé en la fase 1. |

Las series usan `time_s` como tiempo relativo al primer registro calibrado del ensayo y `epoch_ms` para el orden y la identidad temporal. Los nulos se muestran como huecos y la exportación conserva las frecuencias nativas. La alineación de relojes de Cygnus describe la referencia temporal. El retardo físico del sensor requiere evidencia independiente.

## Arquitectura propuesta

CombusLab se plantea como un **monolito modular con Next.js App Router y TypeScript**, desplegado como una sola aplicación sobre Supabase PostgreSQL. Una sola unidad de despliegue reduce el trabajo de integración durante la hackathon y permite compartir reglas y consultas entre pantallas y endpoints.

| Capa | Responsabilidad |
|---|---|
| Presentación | Páginas de servidor para el catálogo y las fichas. Componentes de cliente para filtros, selección de ensayos y gráficos. |
| Aplicación | Módulos para catálogo, series, comparación, escenarios, exportación y resúmenes. Las páginas usan los módulos directamente y el navegador realiza operaciones interactivas mediante Route Handlers. |
| Datos e integraciones | Consultas SQL parametrizadas y tipadas, migraciones, acceso de solo lectura a Supabase y adaptador al proveedor de IA. Python y DuckDB se usan para preparar y validar datos fuera del proceso web. |

PostgreSQL realiza los filtros, la paginación y el recorte por ensayo, ventana y canal. La clave existente cubre las consultas por ensayo y tiempo absoluto. El posible índice `(experiment_id, time_s)` se evalúa con `EXPLAIN` sobre consultas representativas. Las descargas grandes se transmiten por lotes con orden estable. Una gráfica agregada informa de la reducción y la descarga conserva la resolución de la selección.

El servidor valida los filtros y canales, utiliza un rol de lectura con permisos y políticas RLS acordes al acceso de la aplicación y conserva las credenciales fuera del cliente. La consulta científica funciona aun cuando el proveedor de IA esté indisponible. [Backend for Frontend de Next.js](https://nextjs.org/docs/app/guides/backend-for-frontend) · [RLS en Supabase](https://supabase.com/docs/guides/database/postgres/row-level-security)

## Requisitos funcionales

| ID | Capacidad prevista |
|---|---|
| RF-01 | Búsqueda y filtros combinables por material, combustible, objetivo, sensor, resultado, hardware, gravedad, oxígeno, presión y flujo según la cobertura comprobada. La interfaz muestra unidades y valores ausentes, y distingue presión total de presión parcial de O₂. |
| RF-02 | Fichas de investigación y ensayo con objetivo, muestra, geometría, hardware, variables controladas y medidas, sensores, resultados y limitaciones. Las fichas enlazan a PSI e incluyen DOI, versión y localizador cuando estén disponibles. |
| RF-03 | Resúmenes con IA en tres apartados. Objetivo físico, hallazgos clave e implicaciones para misiones espaciales. La pantalla identifica mediciones, conclusiones publicadas e inferencias. El servidor recupera evidencia por identificador, valida las citas contra el contexto enviado y limita el tiempo y la frecuencia de las solicitudes. |
| RF-04 | Comparación de dos o más ensayos. Las series se superponen cuando sus variables, unidades y referencias temporales son compatibles. Las tablas paralelas explican las diferencias de método, instrumentación, entorno y condiciones. |
| RF-05 | Ranking reproducible para un escenario definido por gravedad, oxígeno, presión, flujo, material y pregunta de seguridad. El resultado explica coincidencias, diferencias y datos faltantes. La puntuación mide relevancia de la evidencia. |
| RF-06 | Exploración de combustión e inflamabilidad de sólidos con SAFFIRE y BASS/BASS-II. Los demás ejes del reto se contemplan como ampliaciones y referencias editoriales. |
| RF-07 | Descarga en CSV o JSON de la selección con identificadores, filtros, unidades y procedencia. El CSV puede ir acompañado de un diccionario de datos. Los valores medidos, derivados y límites publicados conservan su calificación. |

## Calidad y aceptación

| ID | Criterio de calidad |
|---|---|
| RNF-01 | Las cifras y conclusiones científicas tienen referencias comprobables y localizadores cuando existan. El resumen declara las lagunas de evidencia. |
| RNF-02 | Las pantallas distinguen medición directa, análogo experimental, modelo y estudio planificado. El escenario lunar de 32 % de O₂ y 10,2 psi es un ejemplo configurable de consulta. |
| RNF-03 | La interfaz funciona en escritorio y móvil, admite navegación por teclado y comunica estados con texto además de color. Controles, ejes, tablas y exportaciones muestran unidades. |
| RNF-04 | Los filtros y gráficos se actualizan sin recargar la página. Las consultas acotan el volumen y la interfaz contempla carga, errores y resultados vacíos. La demo registra latencia y volumen de una consulta representativa. |

| Historia | Comprobación de aceptación |
|---|---|
| US-01 | Una combinación conocida devuelve coincidencias verificables. La búsqueda con O₂ superior a 30 % y presión próxima a 10,2 psi muestra los resultados válidos o explica la ausencia de coincidencias. |
| US-02 | La ficha BASS-II presenta condiciones y procedencia. Una ficha SAFFIRE-III abre la ventana temporal del ensayo seleccionado. |
| US-03 | Un resumen muestra los tres apartados, cita las fuentes y señala una cifra que la evidencia disponible deja sin resolver. |
| US-04 | Dos series compatibles pueden compararse. Una comparación BASS–SAFFIRE identifica las diferencias de magnitud, hardware o método que condicionan la lectura. |
| US-05 | Los escenarios lunar y marciano muestran lagunas de gravedad y atmósfera, con criterios de relevancia visibles. |
| US-06 | La sección de transferencia terrestre enlaza fuentes sobre detectores de humo, indumentaria de protección y tanques de aire. |

La verificación final incluye el orden y unicidad de una ventana real, equivalencia de la descarga con la selección, permisos del rol de aplicación y estados de error de red y del proveedor de IA. La entrega contempla el aplicativo ejecutable, instrucciones de arranque, variables de entorno sin secretos, migraciones, matriz de trazabilidad y guion de demo para el jurado.

## Referencias del proyecto

- [Documentación de los datasets](../datasets/README.es.md)
- [Mapa de nombres de columnas en PostgreSQL](../datasets/supabase_column_map.csv)
- [Contexto científico y fuentes de NASA](../CONTEXTO_NASA.md)
- [English version](PLAN_DEL_SISTEMA.en.md)

## Fases de desarrollo

| Fase | Prioridad | Trabajo | Criterio de salida |
|---|---|---|---|
| 1. Base y contrato de datos | MVP | Inicialización de Next.js, conexión de lectura, carga de metadatos y validación de claves, unidades y permisos. | El servidor devuelve una ficha BASS-II y la ventana de 0 a 60 s de `PSI-100:S1:r2`. |
| 2. Catálogo, fichas y series | MVP | Búsqueda, filtros, fichas trazables y gráficos con cobertura por canal. | Una ficha BASS-II y una gráfica SAFFIRE-III muestran sus fuentes y unidades. |
| 3. Comparación y exportación | MVP | Comparaciones compatibles, avisos metodológicos y descargas CSV o JSON. | Una comparación BASS–SAFFIRE explica sus diferencias y la descarga coincide con la selección. |
| 4. Escenarios e IA | MVP | Ranking determinista y resúmenes con citas verificables. | El escenario lunar expone sus lagunas y el catálogo funciona durante un fallo de IA. |
| 5. Pruebas y demo | MVP | Validación desplegada, revisión de rendimiento y accesibilidad, transferencia terrestre y preparación del guion. | El equipo completa la demo con datos reales y registra el cumplimiento de los requisitos. |
| 6. Nuevas investigaciones | Posterior | Evaluación de SoFIE, SAME/SAME-R y FLEX/FLEX-2. | Cada incorporación cuenta con procedencia, unidades, esquema y validación reproducible. |
