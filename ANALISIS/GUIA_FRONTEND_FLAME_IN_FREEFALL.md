# Flame in Freefall | Guía de implementación del frontend

**Equipo:** Team Changeme  
**Actualización:** 14 de noviembre de 2026  
**Uso:** especificación para la persona o IA que implementará el dashboard web. Los RF, RNF e historias provienen de las notas originales del equipo. Las rutas, el contrato de datos, la interfaz y la secuencia de trabajo se proponen en esta guía.

Lee primero [el contexto general del proyecto](./CONTEXTO_FLAME_IN_FREEFALL.md) y abre [el CSV de BASS-II M7](../datasets/bass_ii_m7.csv). Consulta la rama de trabajo antes de elegir herramientas o implementar vistas.

## 1. Producto y estado actual

El reto [Flame in Freefall de NASA Space Apps](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/) pide un dashboard interactivo que ayude a **resumir, ordenar e interpretar** investigaciones de combustión en microgravedad. La pregunta central de la interfaz es **¿qué estudió NASA, qué resultados sirven para mi consulta y qué límites tiene esa evidencia?** La base de datos científica principal es [NASA PSI](https://psi.nasa.gov/physci/repo/search?q=combustion).

| Insumo o decisión | Estado al redactar esta guía |
| --- | --- |
| Repositorio | Consulta la rama de trabajo. Los CSV documentados aquí son M7 de BASS-II y cuatro ensayos de SIBAL del BASS original. |
| Datos tabulados disponibles | BASS-II: cuatro pares de flujo y tasa dentro de **un mismo ensayo** M7. BASS original: condiciones de cuatro ensayos de SIBAL, con flujo y O₂. |
| Otras investigaciones | Se pueden incorporar fichas editoriales al verificar sus metadatos, hallazgos y enlaces. SAME-R, SoFIE y FLEX-2 son candidatos. Las mediciones de otras fichas requieren curación propia. |
| Lista seleccionada por el equipo | Jaider indicó que la selección y un resumen de NASA están en `G1_NASA2026`. Ese archivo no estaba disponible al preparar esta guía. Si llega a la rama, úsalo para confirmar el catálogo con el equipo. |
| Herramientas e idioma | Pendientes de acordar. Si la rama sigue vacía, React + TypeScript + Vite es una opción para el prototipo. Redacta la interfaz en español durante el desarrollo y confirma el idioma y formato de entrega con el equipo. Centraliza los textos para poder traducirlos. |
| Entrega | Para el hackathon, consulta el [calendario](https://www.spaceappschallenge.org/2026/) y la [guía de entrega](https://www.spaceappschallenge.org/resources/). |

**Audiencias.** Ingeniería y planificación consultan condiciones y vacíos. Investigación necesita método, unidades, comparación y exportación. Estudiantes y docentes necesitan resúmenes en lenguaje claro, glosario contextual y acceso a la fuente.

**Recorridos de demostración.** Buscar BASS-II, abrir M7, ver el gráfico y ubicar la fuente. Luego comparar fichas y explicar si comparten una métrica. Por último, consultar un escenario lunar y mostrar qué tipo de evidencia existe en el catálogo. El producto admite varios recorridos y temas.

> **Datos vigentes para implementación.** El dashboard local usa los JSON de [la documentación de datasets](../datasets/README.md). Incluyen toda la tabla 5.1, la tabla 7.1, la tabla 2.1 y resultados del apéndice D. El CSV de M7 es la extracción piloto. Los ejemplos que lo mencionan conservan su valor como prueba de la primera ficha.

## 2. Navegación y comportamiento por pantalla

| Pantalla y ruta propuesta | Contenido mínimo | Acciones y estados |
| --- | --- | --- |
| **Explorar** `/` | Buscador, filtros de tema, combustible/material, gravedad y hardware. Filtros numéricos de O₂, presión y flujo según la cobertura. Total real de resultados. Tarjetas con nombre, ID, fenómeno, combustible, entorno y nivel de cobertura. | Aplicar, quitar y limpiar filtros. Abrir ficha. Agregar a comparación. Mostrar carga, error de lectura, catálogo vacío o filtros sin coincidencias con acciones distintas. |
| **Ficha** `/estudios/:id` | Objetivo, variables controladas y medidas, material o combustible, forma y dimensiones, instalación, método, instrumentos, condiciones, resultados y límites. Tabla y gráfico si hay series. Enlaces a PSI y a publicaciones con localizador. | Abrir fuentes, elegir ensayo si hay varios, comparar, exportar y solicitar explicación de IA cuando el servicio esté disponible. Si solo hay metadatos, mostrar **Mediciones pendientes de incorporar**. Un ID desconocido ofrece volver a Explorar. |
| **Comparar** `/comparar` | Dos selecciones distintas para el primer flujo, tabla alineada por variable, unidades, método, diferencias, evidencia y fuentes. La propuesta amplia admite más estudios si se implementa posteriormente. | Agregar y quitar estudios, sustituir una selección, avisar el motivo concreto de una incompatibilidad. Con una sola selección, indicar cómo añadir la segunda. Sin métrica comparable, conservar la tabla y explicar el motivo. |
| **Escenarios** `/escenarios` | Plantillas de cabina en microgravedad, hábitat lunar y hábitat marciano, además de un escenario editable. Formulario para fenómeno, material, gravedad, O₂, presión y flujo. Lista ordenada por relevancia, con coincidencias, diferencias, vacíos y fuentes. | Elegir plantilla, editar parámetros, ejecutar consulta y abrir fichas. Los valores de ejemplo se identifican como hipotéticos, como 32 % de O₂ a 10,2 psia para el escenario lunar de las notas. Si faltan datos directos, mostrar qué tipo de evidencia hay y qué queda por comprobar. |
| **Fuentes y aplicaciones** `/fuentes` | Fuentes de datos, contexto histórico y aplicaciones terrestres enlazadas. | Ir a PSI, NTRS, material divulgativo o NASA Spinoff. Identificar el propósito de cada fuente. |

Conserva el estado de búsqueda y filtros al volver desde una ficha. Propón parámetros de URL para filtros o selecciones que convenga compartir. En móvil, permite abrir y cerrar filtros, apila los detalles de las fichas y usa desplazamiento localizado para tablas anchas. Evita que una tabla desplace toda la página.

**Patrones de interacción.** Cada tarjeta lleva a una ficha. El mismo control de comparación aparece en catálogo y ficha. Indica cuántos estudios están seleccionados cuando ese dato ayuda a actuar. Muestra **Sin dato** junto a una variable desconocida y explica el motivo si se conoce. Diferencia el error técnico, la falta de evidencia y la ausencia de coincidencias.

**Diseño propuesto.** Usa un dashboard científico con jerarquía clara, espacio para tablas y fondo de alto contraste. Instrument Sans o Inter para texto y numerales tabulares para mediciones. Usa color y texto juntos para identificar tipos de evidencia, alertas y selección. Las imágenes son opcionales. Si una imagen experimental aporta información, muestra su crédito y fuente.

## 3. Requerimientos funcionales y aceptación

| ID | Implementación esperada | Criterio de aceptación |
| --- | --- | --- |
| **RF-01 · Búsqueda y filtros facetados** | Buscar por nombre, acrónimo, ID PSI, tema o material. Filtrar por fase del combustible, material, gravedad, hardware, O₂, presión y flujo. | Los filtros se combinan, los resultados muestran entorno, hardware y fase, y se indica qué filtros están activos. Las condiciones numéricas usan la misma definición y unidades. Una combinación solo coincide cuando los criterios pertenecen al mismo ensayo o condición documentada. |
| **RF-02 · Ficha técnica y fuentes** | Mostrar objetivo, muestra o quemador, material, dimensiones, montaje, sensores, condiciones, variables controladas y medidas, hallazgos y límites. | Desde la ficha se abre la URL exacta de PSI cuando está verificada. Los resultados enlazan el reporte, DOI o archivo y llevan página, tabla, figura o fila cuando corresponde. Los campos desconocidos se señalan. |
| **RF-03 · Explicación asistida por IA** | Solicitar explicación del estudio y presentar objetivo físico, hallazgos e implicaciones, con límites y fuentes. | Las afirmaciones concretas incluyen referencias accesibles. Datos experimentales, resultados calculados, simulaciones e interpretación de IA tienen etiquetas visibles y distintas. Hay estados de carga, servicio sin configurar, error, reintento y evidencia insuficiente. |
| **RF-04 · Comparación y compatibilidad** | Seleccionar estudios y alinear material, geometría, método, hardware, gravedad, presión, O₂, flujo y resultados. | La tabla compara dos estudios distintos y señala condiciones que difieren o faltan. El gráfico compartido requiere una magnitud equivalente, unidades compatibles y condiciones interpretables. Se explica cualquier límite del cruce. |
| **RF-05 · Evaluación de escenarios** | Configurar una consulta de cabina, Luna o Marte y ordenar estudios por relevancia. Mostrar el motivo de la posición y los vacíos. | Cada resultado identifica coincidencias, diferencias y desconocidos. En la Luna, distingue medición in situ, ensayo con gravedad parcial simulada, analogía y modelo según lo disponible. La interfaz identifica el orden como relevancia de la evidencia. |
| **RF-06 · Módulos temáticos** | Permitir explorar comportamiento del fuego (SoFIE), inflamabilidad de sólidos (BASS/BASS-II), detección y humo (SAME/SAME-R, DAFT) y combustión de líquidos (FLEX/FLEX-2). | Los cuatro temas son navegables desde un catálogo común. Sólidos muestra M7. Cada tema sin ficha o serie curada declara esa cobertura. Las familias adicionales, como ACME, SPICE y SLICE, se incorporan con fuentes verificadas. |
| **RF-07 · Exportación estructurada** | Descargar las mediciones disponibles de una ficha o de una selección en CSV o JSON. | Para M7, el archivo original ya permite la descarga. Una exportación de selección preserva IDs, valores, unidades, fuentes, localizadores y contexto disponible. Añade método y tipo de evidencia si están documentados. Si el alcance es una selección filtrada, la interfaz indica qué se exporta. |

## 4. Requerimientos no funcionales

| ID | Regla de implementación | Verificación |
| --- | --- | --- |
| **RNF-01 · Trazabilidad y rigor** | Vínculo visible entre cifra, observación o afirmación factual y fuente verificable. Conserva unidades y precisión de la fuente. | Desde un punto de M7 se puede ubicar la fila original. El export conserva esa procedencia. La explicación de IA se comprueba contra referencias del catálogo. |
| **RNF-02 · Transparencia científica** | Visibilizar datos ausentes, límites metodológicos y tipo de evidencia. Identificar escenarios hipotéticos. | Usa valores desconocidos en una prueba y confirma que se muestran como **Sin dato**. En una consulta lunar, verifica que la interfaz indica el alcance de la evidencia. |
| **RNF-03 · Visualización y usabilidad** | Unidades junto a ejes, campos y tablas. Controles con etiquetas, foco visible, navegación por teclado y estados anunciados. Ofrece una tabla legible que reproduce los valores del gráfico. [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Recorre filtro, ficha, comparación y escenario con teclado y en ancho móvil. Verifica contraste, foco, encabezados de tablas y que el gráfico se entienda sin pasar el puntero. |
| **RNF-04 · Rendimiento** | Leer un dataset versionado localmente o a través de una capa de datos. Mantener búsqueda, filtros y comparación dentro de la aplicación. | Cambia filtros y selecciones sin recarga completa ni peticiones a NASA en cada interacción. Comprueba el estado de carga y el comportamiento cuando falla la red. |

## 5. Historias de usuario y pruebas de aceptación

### HU-01 / US-01 · Filtrar por atmósfera operativa
Como ingeniero de soporte vital, quiero filtrar evidencia por O₂ y presión para localizar condiciones cercanas a un escenario de misión.

- Dado un catálogo con condiciones documentadas, al seleccionar intervalos compatibles, veo estudios con al menos un ensayo que satisface el conjunto de condiciones aplicadas. Los extremos se consideran incluidos salvo que el control indique un operador estricto.
- Al fijar un intervalo atmosférico de O₂, el oxígeno de una corriente del quemador se muestra en su propio contexto. Los datos de CFI-G de hasta 85 % se refieren a esa corriente. Si el catálogo incorpora CFI-G, enséñalo en búsquedas pertinentes. [Antecedentes del reto](https://hackathlone.com/challenges/flame-in-freefall)
- Cada resultado muestra combustible y hardware cuando están documentados. Si ningún dato coincide, puedo quitar filtros sin perder la búsqueda.

### HU-02 / US-02 · Consultar la ficha y verificar resultados
Como investigador, quiero abrir una ficha para entender el montaje y consultar la publicación original.

- Al abrir BASS-II, veo PMMA, geometría, flujo opuesto, fuente del estudio y mediciones M7 con unidades.
- Puedo seguir el vínculo a PSI-25 y al informe NASA/TM-20210011385. El resultado indica la tabla 5.1, página impresa 57 y ensayo M7. 
- El acceso al informe y a los datos queda disponible en móvil y mediante teclado.

### HU-03 / US-03 · Entender una investigación con IA
Como estudiante o profesional, quiero solicitar una explicación para entender qué se estudió, qué se observó y qué implicaciones podrían investigarse.

- Con un servicio configurado, la respuesta muestra **Objetivo físico**, **Hallazgos clave** e **Implicaciones para misiones espaciales**, junto a **Límites** y referencias. La interfaz permite abrirlas.
- Si la consulta carece de evidencia, el resultado indica qué faltó. Si el servicio está deshabilitado, puedo leer una ficha editorial identificada como tal y consultar sus fuentes.

### HU-04 / US-04 · Comparar estudios con advertencias
Como investigador de combustión, quiero contrastar dos estudios en paralelo para entender qué diferencias condicionan la comparación.

- Al elegir BASS-II y una ficha de humo como SAME-R, la tabla identifica las diferencias de fenómeno y magnitud. Conserva las fuentes y explica por qué falta un gráfico conjunto.
- Con dos estudios de sólidos compatibles y datos curados, puedo ver las condiciones y sus métricas en unidades comunes. El hardware distinto, el flujo y el oxígeno aparecen como diferencias cuando corresponda.

### HU-05 / US-05 · Identificar vacíos de evidencia lunar y marciana
Como planificador, quiero consultar evidencia en gravedad parcial para distinguir ensayos, modelos y analogías.

- Al seleccionar **Hábitat lunar**, veo los parámetros que completé, la cobertura del catálogo y el tipo de evidencia de cada resultado.
- Si se incluyen fichas verificadas, LUCI se identifica como ensayo con gravedad lunar simulada por rotación, E-FIELD Flames como analogía experimental y FM² como investigación diseñada para mediciones en la superficie lunar. Incorporar resultados de FM² requiere una publicación o dataset verificable. [LUCI](https://ntrs.nasa.gov/citations/20250010653) · [E-FIELD](https://science.nasa.gov/biological-physical/investigations/e-field-flames/) · [FM²](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-of-materials-on-the-moon-fm2/)
- Si el catálogo carece de mediciones directas para las condiciones elegidas, muestra **Sin evidencia directa en este catálogo** y las diferencias relevantes de los estudios disponibles.

### HU-06 / US-06 · Consultar aplicaciones terrestres
Como docente, divulgador o evaluador, quiero conocer aplicaciones terrestres de la investigación espacial.

- La sección de fuentes y aplicaciones presenta ejemplos de detector que distingue humo y polvo, equipos respiratorios o tanques de aire, e indumentaria de bomberos, con su aplicación documentada. [Detector](https://spinoff.nasa.gov/node/9407) · [Tanques de aire](https://spinoff.nasa.gov/node/9582) · [Indumentaria](https://spinoff.nasa.gov/node/9918)

## 6. Datos y gráfico que ya se pueden implementar

Lee [`datasets/bass_ii_m7.csv`](../datasets/bass_ii_m7.csv) como fuente de verdad del prototipo. Cada fila corresponde a un punto de flujo y tasa dentro de M7. El registro de ensayo agrupa las cuatro filas por `investigation_id` y `run_id`. Usa un identificador derivado del ensayo y el punto para las filas de la interfaz. Comprueba el encabezado y que las magnitudes sean numéricas al importar.

| Columnas reales | Uso en la interfaz |
| --- | --- |
| `investigation_id`, `run_id`, `material` | Identificar PSI-25, M7 y PMMA. |
| `sample_thickness_mm`, `sample_width_cm`, `burning_sides` | Características de la muestra, con unidad y dos caras en combustión. |
| `opposed_airflow_cm_s`, `flame_spread_rate_mm_s` | Ejes X e Y respectivamente. Incluir ambos valores y unidades en el detalle del punto. |
| `run_initial_oxygen_vol_pct`, `run_final_oxygen_vol_pct` | O₂ inicial y final del ensayo completo. Mostrar una vez en el resumen de M7. Para un filtro por condición exacta de O₂, M7 carece de un valor documentado por punto en el CSV. |
| `source_report`, `source_table`, `source_printed_page`, `source_url` | Mostrar informe, tabla, página impresa y enlace. Conservar la tabla como identificador de texto. |

**Gráfico inicial.** Diagrama de dispersión de flujo de aire opuesto (cm/s) frente a velocidad de propagación de la llama (mm/s). Mostrar cuatro puntos en el eje X por valor numérico y una tabla accesible con esos mismos datos. El informe reporta para M7 los pares `3 / 0.07`, `5 / 0.083`, `6 / 0.099` y `10 / 0.106`. Mantén decimales con punto al importar o exportar el CSV y usa formato local en la interfaz. El gráfico describe este ensayo. El O₂ cambió durante la prueba y el CSV solo registra su valor inicial y final. [NASA/TM-20210011385, tabla 5.1](https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf)

**Contrato normalizado propuesto para crecer.**

- `Investigation`: ID PSI, título, familia, temas, fase del combustible, plataforma y equipo, objetivo, entorno, variables, hallazgos documentados, límites y fuentes.
- `Run`: ID del estudio y ensayo, material, geometría, método, condiciones de ensayo, serie y fuentes. `DataPoint`: condición identificable, métricas y enlace al ensayo. Mantén condiciones del ensayo fuera de los campos por punto cuando la fuente solo las reporta para todo el ensayo.
- `Measurement`: magnitud, valor, unidad original, método, incertidumbre cuando exista y fuente. Magnitudes con el mismo símbolo de unidad pueden requerir métodos distintos.
- `Source`: URL, título, ID del reporte o DOI, página impresa y localizador según disponibilidad. El enlace PSI-25 identifica el estudio. El informe NTRS documenta el dato.
- `Scenario`: entorno, fenómeno, material, gravedad, oxígeno, presión, flujo y procedencia de los valores. Registra si el escenario es hipotético o documentado.
- Para un valor desconocido usa `null`. Preserva el cero explícito y registra método, unidad y alcance al normalizar. Distingue presión absoluta, O₂ ambiental y O₂ de corrientes de alimentación. Un rango inicial/final puede informarse como contexto y requiere una regla explícita si se usa en filtros.

**Cobertura inicial.** PSI-25 tiene datos tabulares del equipo. Una ficha adicional puede contener datos editoriales respaldados y estar marcada **Solo ficha**. [SAME-R, PSI-101](https://psi.nasa.gov/physci/repo/data/investigations/PSI-101), [SoFIE](https://science.nasa.gov/biological-physical/investigations/sofie/) y [FLEX-2](https://www.nasa.gov/wp-content/uploads/2025/07/flame-extinguishment-experiment-flex.pdf) ofrecen puntos de partida. Los datos de prueba sintéticos se limitan a pruebas automatizadas o manuales separadas del catálogo publicado.

**BASS original.** [El CSV de SIBAL](../datasets/bass_sibal_concurrent.csv) recoge los cuatro ensayos de BASS identificados en la tabla 7.1, página impresa 96. Registra ancho de muestra, flujo concurrente y O₂. La tabla 7.1 reporta condiciones de ensayo y omite valores tabulados de velocidad de propagación. En el comparador, muestra estas condiciones y la procedencia. BASS usa tejido SIBAL en flujo concurrente en esta selección y M7 usa PMMA en flujo opuesto, por lo que sus datos requieren visualizaciones independientes.

## 7. Reglas de comparación, escenarios e IA

### Comparación

1. La tabla lado a lado funciona con cualquier par de fichas distintas. Describe las diferencias de fenómeno, combustible, hardware, método, geometría, gravedad, oxígeno, presión y flujo según disponibilidad.
2. Habilita un gráfico conjunto solo cuando ambas series describan la misma magnitud con unidades compatibles, método y condiciones interpretables. Si falta una variable crítica, muestra **Información insuficiente para graficar juntas** y el campo faltante.
3. Diferencias de montaje o material se reportan de forma concreta, por ejemplo, «Tasa de propagación en un sólido y tamaño de partículas de humo son resultados distintos». Una tasa en mm/s y una constante de combustión de gotas en mm²/s tienen gráficos propios.

### Ranking para escenarios

1. Da prioridad al fenómeno. Luego evalúa coincidencia de material o fase y régimen gravitatorio. Usa presión, O₂, flujo y geometría como información secundaria cuando se puedan comparar. Describe para cada criterio **Coincide**, **Difiere** o **Sin dato**.
2. Para la primera demo, usa grupos ordenados con reglas visibles: fenómeno y condiciones pertinentes coincidentes, evidencia relacionada con diferencias, y cobertura insuficiente cuando falten datos decisivos. Dentro de cada grupo ordena por material/fase, gravedad y número de condiciones secundarias coincidentes, con desempate por ID. Aplica estas reglas de forma estable a la misma entrada. Para números, documenta la unidad y compara dentro del rango que el usuario especifique. A falta de rango, presenta el valor reportado y la diferencia sin inventar tolerancias.
3. Registra por separado el tipo de evidencia. La etiqueta **Directa para el escenario** requiere método y condiciones pertinentes documentadas. Una coincidencia parcial o analogía conserva su explicación propia. El orden representa relevancia para la búsqueda. Limita la interfaz a apoyo para explorar evidencia científica.

### Integración de IA

- La ficha de datos y la explicación son componentes distintos. El frontend pasa al servicio los IDs seleccionados y la pregunta, o el escenario estructurado. El backend recupera fichas y extractos citables. El contrato propuesto incluye `status`, `objective`, `findings`, `implications`, `limitations` y referencias por afirmación con ID de fuente y localizador.
- Usar estados `loading`, `success`, `insufficient_evidence`, `unavailable` y `error`. Evidencia insuficiente explica el vacío. Error ofrece reintento. Servicio no configurado muestra el resumen editorial identificado y preserva el acceso al catálogo.
- Las credenciales pertenecen al backend. Valida la forma de la respuesta y resuelve los enlaces desde las fuentes conocidas. Trata citas no resolubles como un fallo de validación. Presenta texto y enlaces verificables sin ejecutar contenido del proveedor.
- El ranking determinista se puede implementar con el catálogo versionado. Una explicación con IA debe usar los mismos IDs, tipos de evidencia y criterios visibles de ese resultado.

## 8. Fuentes para el producto

| Uso | Fuentes |
| --- | --- |
| Datos y método experimental | [NASA PSI, combustión](https://psi.nasa.gov/physci/repo/search?q=combustion) · [Índice PSI](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/) · [PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) · [BASS-II en NTRS](https://ntrs.nasa.gov/citations/20210011385) |
| Introducción científica | [Combustion Science de NASA Glenn](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/) · [Guía de investigadores sobre combustión en la EEI](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/) · [NASA ScienceCasts](https://www.youtube.com/watch?v=W1oXykoz9zg) |
| Contexto de seguridad espacial | [Apolo 1](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) · [Apolo 13](https://sma.nasa.gov/sma-disciplines/accllp/apollo-13) · [Incendio en Mir](https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/) |
| Alcance del reto | [NASA Space Apps](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/) · [Antecedentes y recursos en HackAthlone](https://hackathlone.com/challenges/flame-in-freefall) |

Aplica los términos de uso y atribución de cada fuente, en particular de sitios de terceros. El reto indica que NASA no respalda a entidades ajenas al Gobierno de Estados Unidos ni se responsabiliza por el contenido de sus sitios. Identifica el dashboard como proyecto de Team Changeme para el reto y atribuye el material a su fuente. Los antecedentes históricos y las aplicaciones son contexto editorial. Las mediciones del dashboard se vinculan a su evidencia experimental.

## 9. Orden de implementación y criterio de entrega

1. **Primer recorrido.** Configura navegación, catálogo, ficha PSI-25, importación del CSV, gráfico y fuentes. Prueba búsqueda de BASS-II, apertura de la ficha, cuatro puntos y enlace de procedencia.
2. **Exploración y comparación.** Añade filtros, los cuatro temas y una segunda ficha con metadatos verificados. Prueba filtros combinados, estados vacíos y una comparación metodológicamente distinta. Agrega una comparación cuantitativa entre estudios cuando haya dos series curadas.
3. **Escenarios.** Implementa el formulario, ranking y explicación de criterios. Prueba cabina ventilada y Luna. Una consulta marciana sin datos directos debe mostrar la cobertura real y seguir permitiendo explorar las fuentes.
4. **Interpretación, exportación y contexto.** Implementa el contrato de IA, prueba su integración cuando el backend esté listo, habilita la descarga de M7 y la exportación de selecciones si corresponde. Incorpora la vista de aplicaciones terrestres.
5. **Verificación integrada.** Recorre catálogo, ficha, comparación y escenarios en móvil y escritorio. Abre y recarga directamente la URL de la ficha para verificar su navegación en el entorno de despliegue. Contrasta valores y unidades con NASA, revisa teclado, enlaces, orden estable, diferencia entre `null` y cero, errores de red y respuesta de IA sin evidencia. Registra por ID lo implementado, los escenarios probados y los pendientes de datos o integración.

El primer entregable demostrable es **buscar BASS-II → consultar M7 → ver el gráfico y la tabla → abrir la fuente**. La entrega completa debe indicar qué RF, RNF y HU están cubiertos y cuáles siguen pendientes de datos curados o de integración.

## 10. Prompt para la IA de frontend

> Trabaja en el repositorio JaiderBadillo/TeamChangeme_Reto_Nasa. Antes de editar, lee ANALISIS/CONTEXTO_FLAME_IN_FREEFALL.md, ANALISIS/GUIA_FRONTEND_FLAME_IN_FREEFALL.md y datasets/bass_ii_m7.csv. Revisa los archivos y convenciones de la rama. Implementa primero la búsqueda, ficha de BASS-II, gráfico y tabla del ensayo M7, con su referencia a NASA. Después sigue el orden de implementación de la guía. Conserva los IDs RF-01 a RF-07, RNF-01 a RNF-04 y HU-01 a HU-06, identificadas también como US en las notas originales. Usa mediciones verificadas, muestra los estados de cobertura, aplica las reglas de compatibilidad y distingue los tipos de evidencia de la explicación de IA. Al terminar, entrega instrucciones reproducibles de ejecución y el estado por requisito e historia, con pruebas realizadas y dependencias pendientes.
