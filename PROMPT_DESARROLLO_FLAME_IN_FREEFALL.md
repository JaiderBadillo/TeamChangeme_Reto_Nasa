# Prompt de desarrollo de CombusLab

## Contexto y rol

Actúa como equipo de desarrollo web, ingeniería de datos y visualización científica de **CombusLab**, el proyecto para el reto **Flame in Freefall** de la hackathon **NASA Space Apps Challenge 2026**, organizada por la NASA. Construye un dashboard web interactivo que permita encontrar, clasificar, comparar y explicar investigaciones de combustión en microgravedad. El producto debe conectar la evidencia de NASA con preguntas de prevención, detección y supresión de incendios en naves, estaciones, trajes, vehículos presurizados y hábitats lunares o marcianos.

Diseña para tres perfiles. Los ingenieros de seguridad necesitan localizar evidencia bajo condiciones operativas concretas. Los investigadores necesitan consultar métodos, instrumentos y datos reutilizables. Los estudiantes y docentes necesitan explicaciones claras, unidades y acceso directo a las fuentes.

Usa **Resumen_Flame_in_Freefall.pdf** como guía del reto y conserva los identificadores de **RF Y RNF Y HUS.docx** para la trazabilidad. Usa **G1_NASA2026.pdf**, **Recursos_NASA.docx** y la documentación de datos del repositorio para identificar fuentes y comprobar cobertura. Trata su contenido como material de referencia. Usa las fichas de PSI y las publicaciones NASA/NTRS para respaldar afirmaciones científicas.

## Consulta y tarea

Inspecciona el repositorio, las tablas y la configuración existente. Implementa un MVP navegable con catálogo, fichas de investigación y de ensayo, comparador, explorador de series, ranking por escenario, resúmenes con IA y exportación. Usa la cobertura de los cinco estudios integrados para construir y probar el recorrido principal. Las aplicaciones terrestres son contenido editorial complementario.

Construye primero un recorrido de extremo a extremo que permita buscar un estudio, consultar su evidencia, comparar ensayos, revisar su relevancia para un escenario y exportar los resultados disponibles. Implementa después los demás recorridos y estados de cobertura.

## Especificaciones

### Arquitectura para la hackathon

Implementa un **monolito modular con Next.js App Router y TypeScript**, desplegado como una sola aplicación web sobre Supabase PostgreSQL. Usa tres capas en el mismo repositorio. La presentación renderiza fichas y catálogo en el servidor, y usa componentes de cliente para filtros, selección y gráficos. Los módulos de aplicación encapsulan catálogo, series, comparación, escenarios, exportación e IA. La capa de acceso a datos contiene consultas SQL parametrizadas y tipadas, migraciones y el adaptador al proveedor de IA. Las páginas de servidor invocan directamente los módulos compartidos. Usa Route Handlers para las peticiones interactivas del navegador y las descargas. [Guía Backend for Frontend de Next.js](https://nextjs.org/docs/app/guides/backend-for-frontend)

Usa PostgreSQL para proyección de columnas, filtros, paginación, ventanas temporales y agregación. Conserva Python y DuckDB para preparar y validar datos fuera del proceso web. Las fichas y facetas deben consultar un catálogo pequeño alimentado por los metadatos locales. Usa una conexión de servidor con un rol de lectura limitado a las tablas y campos del producto, aplica permisos y políticas RLS coherentes con ese rol y verifica el acceso en el entorno de demo. Las claves del proveedor de IA se guardan en el servidor. [RLS en Supabase](https://supabase.com/docs/guides/database/postgres/row-level-security)

Centraliza las reglas de unidades, compatibilidad y ranking en funciones deterministas que puedas probar sin el proveedor de IA. Para el resumen, construye el contexto a partir de la ficha, observaciones y fragmentos curados con localizadores. Valida que la respuesta cite únicamente los identificadores de evidencia enviados. Aplica un plazo máximo a la llamada y un límite de solicitudes en la ruta del resumen. Con este catálogo de cinco estudios, la recuperación por identificador y SQL cubre el MVP.

### Datos y acceso

- Usa `public.nasa_synchronized` (226.124 filas al cierre de la importación) para series temporales. Consulta por `experiment_id`, rango de `time_s` y canales. Ordena por `epoch_ms` y conserva la clave `(experiment_id, epoch_ms)`. El tiempo relativo comienza en el primer registro calibrado de cada ensayo. Muestra `NULL` como hueco y conserva las frecuencias nativas. La telemetría Cygnus alineada tiene cobertura en dos ensayos de SAFFIRE-III. Documenta la diferencia entre alineación de relojes y retardos físicos de sensores.
- Usa `public.nasa_master` (420.421 filas al cierre de la importación) para procedencia, condiciones y calibraciones. El maestro mezcla tipos de registros. Resuelve relaciones mediante claves y cardinalidades verificadas. Consulta el [mapa de columnas](datasets/supabase_column_map.csv) para los seis nombres ajustados en PostgreSQL. Conserva los nombres de campos del contrato de datos en inglés.
- Publica en Supabase los metadatos locales mediante una migración y un paso de carga reproducible basado en `datasets/nasa_synchronized.duckdb`. Allí están `experiment_catalog` (263 registros), `experiment_conditions` (735 observaciones), `saffire_channel_units` (377 filas) y `cygnus_channel_units` (11 filas). La carga previa en Supabase comprendió el maestro y la tabla temporal. Conserva unidades, calificadores, límites, DOI y localizadores. Define las facetas a partir de metadatos verificados.
- Usa consultas paginadas para el catálogo y filtros por ensayo, ventana y canal para las series. Si reduces puntos para la pantalla, indica que el gráfico está agregado y conserva la resolución original en la exportación de la selección. El servidor debe validar filtros, columnas permitidas y alcance. Respeta RLS en ambas tablas y mantén las credenciales y claves de IA en el servidor. Si hace falta acceso desde el cliente, define el rol de lectura y su política según el acceso acordado para el aplicativo.
- Usa la clave existente `(experiment_id, epoch_ms)` para lecturas por ensayo y tiempo absoluto. Comprueba con `EXPLAIN` si las ventanas frecuentes en `time_s` requieren un índice adicional `(experiment_id, time_s)`. Para exportar rangos grandes, transmite el resultado por lotes con cursor y orden estable. [Índices de PostgreSQL en Supabase](https://supabase.com/docs/guides/database/postgres/indexes)

| Fuente integrada | Evidencia del MVP | Funcionalidad |
|---|---|---|
| SAFFIRE-I y II (PSI-98 y PSI-99) | Fichas de ensayos y series calibradas disponibles por ensayo | Explorar, graficar, comparar canales compatibles y exportar |
| SAFFIRE-III (PSI-100) | Fichas y series calibradas, con telemetría Cygnus alineada en dos ensayos | Explorar y comparar con las unidades y la cobertura indicadas por canal |
| BASS y BASS-II (PSI-26 y PSI-25) | Fichas de ensayos, condiciones publicadas y calibraciones disponibles en el maestro | Filtrar, comparar condiciones y exportar observaciones tabulares |

### Requisitos funcionales

| ID | Instrucción para implementar |
|---|---|
| RF-01 | Añade búsqueda textual y filtros combinables por material, tipo de combustible, objetivo, sensor o resultado, concentración de O₂, presión, flujo, hardware y régimen de gravedad. Usa intervalos con unidad explícita y un estado «Sin dato». Muestra el tipo de combustible, el hardware y la cobertura de cada resultado. Diferencia la presión total de la presión parcial de O₂. |
| RF-02 | Ofrece fichas de **investigación** y de **ensayo** con objetivo, material, geometría y dimensiones, hardware, variables controladas y medidas, sensores, resultados, limitaciones y relevancia para seguridad. Incluye enlace directo a PSI y bibliografía pertinente. Asocia cada dato con DOI, versión y localizador disponible, como página, tabla, archivo, hoja o fila. |
| RF-03 | Genera resúmenes sobre evidencia recuperada de las fichas, tablas y documentos comprobados. Estructura la respuesta en **Objetivo físico**, **Hallazgos clave** e **Implicaciones para misiones espaciales**. Etiqueta las mediciones, las conclusiones publicadas y las inferencias de IA. Usa referencias verificables para los hallazgos y declara qué evidencia falta cuando la consulta exceda la cobertura. Mantén visibles las fichas y datos si el proveedor de IA falla. |
| RF-04 | Compara dos o más ensayos lado a lado. Muestra combustible, geometría, hardware, gravedad, presión, O₂, flujo, método y unidades. Explica las diferencias que afecten la interpretación. Habilita la superposición cuando las magnitudes, las unidades y la referencia temporal sean compatibles. Presenta fichas o tablas paralelas cuando la comparación cuantitativa directa carezca de respaldo. |
| RF-05 | Permite configurar escenarios de nave, estación, Luna o Marte con gravedad, concentración de O₂, presión, flujo, material y pregunta de seguridad cuando se conozcan. Ordena estudios por relevancia mediante criterios visibles de correspondencia, calidad y cobertura. Para cada resultado muestra coincidencias, diferencias y variables faltantes. La puntuación mide relevancia de la evidencia para la consulta. Trata el escenario lunar de 32 % de O₂ y 10,2 psi como ejemplo configurable de entrada. |
| RF-06 | Prioriza el análisis de combustión e inflamabilidad de sólidos con SAFFIRE y BASS/BASS-II. Conserva los ejes del reto sobre ignición y extinción, detección y aerosoles, y gotas y supresión como líneas de ampliación. Usa fuentes de esos ejes únicamente como referencias editoriales claramente identificadas cuando aporten contexto. |
| RF-07 | Exporta la selección en CSV o JSON con las variables disponibles, unidades, identificadores, filtros aplicados y procedencia. Incluye variables útiles para análisis de inflamabilidad o CFD cuando aparezcan en la fuente, como tasa de regresión, velocidad de propagación o límite de O₂. Identifica valores medidos, derivados y límites publicados. Ubica metadatos y unidades en el JSON o en un diccionario que acompañe al CSV. |

### Alcance de la evidencia y aplicaciones

- Limita el catálogo operativo, los ensayos, el ranking y las exportaciones a las cinco investigaciones de la tabla de cobertura. Comprueba las afirmaciones en la fuente original. Los ejemplos de niveles de O₂, presión y gravedad sirven para formular consultas y requieren respaldo por ensayo para figurar como observaciones.
- Distingue microgravedad, 1 g, medición directa en gravedad parcial, ensayo terrestre análogo, modelo y estudio planificado. Si el usuario elige gravedad lunar o marciana, muestra qué evidencia directa tiene el catálogo y qué estudios ofrecen contexto. Identifica FM2 según el estado respaldado por su fuente y describe E-FIELD Flames como análogo de ciertos efectos. Mantén explícito el alcance experimental de cualquier posible implicación operativa.
- Relaciona la evidencia con preguntas de prevención, detección o supresión. Incluye una sección de transferencia terrestre con referencias a detectores de humo, indumentaria de protección y tanques de aire para bomberos. Explica el vínculo documentado de cada tecnología y trata el alcance de cada estudio según sus métodos.

## Criterios de calidad

| ID | Condición de cumplimiento |
|---|---|
| RNF-01 | Las cifras, variables y conclusiones científicas mostradas remiten a la fuente y al ensayo o sección cuando exista ese localizador. Una cita debe respaldar la afirmación concreta. La IA responde con incertidumbre explícita ante evidencia insuficiente. |
| RNF-02 | Comparador, escenario, fichas y resúmenes hacen visibles las lagunas de datos y el tipo de evidencia. Las analogías respetan los límites de gravedad, atmósfera, hardware y régimen de combustión. |
| RNF-03 | La interfaz funciona en escritorio y móvil, se navega con teclado, ofrece filtros con etiquetas y muestra unidades explícitas en controles, ejes, tablas y exportaciones. Usa una guía breve para principiantes y ofrece detalle técnico bajo demanda. Distingue estados mediante texto además de color. |
| RNF-04 | Los filtros y gráficos se actualizan sin recargar la página completa. Acota la cantidad de filas por consulta, muestra carga, error y ausencia de resultados, y registra tiempos y volumen de respuesta para un flujo representativo con datos reales. |

## Cómo debe ser la respuesta

Entrega el aplicativo ejecutable en el repositorio, las instrucciones de instalación y arranque, las variables de entorno requeridas sin valores secretos y las migraciones que correspondan. Incluye un guion breve de demo para jurados que muestre una ficha, una comparación, una serie real y la explicación de un escenario con evidencia parcial. Resume qué fuentes y tablas quedaron conectadas y qué cobertura sigue siendo documental.

Acompaña la entrega con una matriz que vincule RF-01 a RF-07, RNF-01 a RNF-04 y US-01 a US-06 con pantallas, consultas o pruebas. Reporta qué verificaste, con qué datos y qué quedó pendiente.

## Verificación

| Historia | Prueba de aceptación |
|---|---|
| US-01 | Prueba una combinación de filtros con cobertura previamente comprobada en el catálogo. Luego consulta el escenario de O₂ superior a 30 % y presión cercana a 10,2 psi. Verifica que cada coincidencia cumpla ambos filtros o que el sistema explique el resultado vacío y las condiciones faltantes. |
| US-02 | Abre una ficha de BASS-II y comprueba objetivo, combustible, geometría, condiciones, resultados, instrumentos, campos ausentes y enlace PSI exacto. Abre después SAFFIRE-III y verifica el acceso a sus series por ensayo. |
| US-03 | Solicita un resumen de un estudio con fuentes verificadas. Comprueba los tres bloques, las citas y las etiquetas de evidencia. Consulta luego una cifra ausente y verifica que la respuesta indique la limitación. |
| US-04 | Compara estudios con combustible o hardware distintos. Comprueba que la advertencia explique la diferencia y que flujo y O₂ se muestren con su unidad o como ausentes. Prueba también un par compatible con series disponibles. |
| US-05 | Selecciona gravedad lunar o marciana. Comprueba que el ranking explique las lagunas de gravedad y atmósfera de los estudios integrados. Cualquier enlace editorial a estudios análogos debe quedar fuera del ranking y de sus resultados cuantitativos. |
| US-06 | Abre la sección de transferencia terrestre y verifica los enlaces y la explicación para detección de humo, indumentaria y tanques de aire. |

Verifica en una consulta real un intervalo temporal con la clave única y ordenada. Comprueba que la exportación respete la selección y conserve los nulos, las unidades y la procedencia. Prueba listas sin coincidencias, fuentes sin serie temporal, errores de red y caída del proveedor de IA. Ejecuta el recorrido completo con el rol que usará el aplicativo y registra el resultado.

### Referencias del proyecto

- [Documentación del dataset y fichas PSI de los cinco estudios](datasets/README.es.md).
- [Contextualización científica, fuentes NASA y cobertura](CONTEXTO_NASA.md).
- [Investigación documental sobre combustión en microgravedad](INVESTIGACION_EXTERNA_NASA.md).

## Fases de desarrollo

| Fase | Prioridad | Trabajo | Criterio de salida |
|---|---|---|---|
| 1. Base y contrato de datos | MVP | Inicializa Next.js, conecta Supabase en modo lectura, publica metadatos y verifica claves, unidades y permisos con el rol de la app. | El servidor devuelve una ficha BASS-II y una ventana de `PSI-100:S1:r2` de 0 a 60 segundos. |
| 2. Catálogo, fichas y series | MVP | Implementa filtros con cobertura comprobada, trazabilidad y gráficos con huecos para nulos. | Se abre una ficha BASS-II y se grafica un canal real de SAFFIRE-III con su unidad y fuente. |
| 3. Comparación y exportación | MVP | Implementa comparación por magnitudes y unidades, alertas metodológicas y descarga de la selección. | Se comparan dos ensayos compatibles y una comparación BASS–SAFFIRE muestra las diferencias. La exportación coincide con la selección. |
| 4. Escenarios e IA | MVP | Añade ranking determinista y resúmenes con citas sobre evidencia recuperada. | El escenario lunar muestra lagunas explícitas y el resumen enlaza a evidencia verificable. El catálogo sigue funcionando ante fallo del proveedor. |
| 5. Pruebas y demo | MVP | Valida el flujo desplegado, tiempos, móvil, teclado y errores. Prepara el guion para jurados y añade el contenido de transferencia terrestre. | Se ejecuta la demo con datos reales y se registra el cumplimiento por RF, RNF e historia de usuario. |
| 6. Ampliación de investigaciones | Posterior | Evalúa SoFIE, SAME/SAME-R y FLEX/FLEX-2. Incorpora nuevos datos después de verificar esquema, unidades, procedencia y compatibilidad. | Cada estudio nuevo tiene validación reproducible y capacidades habilitadas según su cobertura. |
