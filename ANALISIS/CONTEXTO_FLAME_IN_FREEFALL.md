# Flame in Freefall | Contexto del proyecto

**Equipo:** Team Changeme  
**Evento:** NASA Space Apps Challenge 2026  
**Actualización:** 14 de noviembre de 2026  
**Estado:** planificación y revisión de fuentes. Los requisitos y el alcance del MVP de este documento son propuestas para el equipo. El stack, el reparto y el estado de cualquier trabajo fuera de este repositorio están pendientes de confirmación.

Este archivo reúne la hoja de ruta, las notas de requisitos, el resumen del reto y las fuentes revisadas. Úsalo al iniciar una sesión con una IA o al asumir una tarea del proyecto.

## Objetivo y alcance

El reto [Flame in Freefall](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/) pide un dashboard web interactivo asistido por IA que **resuma, ordene e interprete** investigaciones de combustión en microgravedad. La base científica principal es [Physical Sciences Informatics (PSI)](https://psi.nasa.gov/physci/repo/search?q=combustion) de NASA. El reto usa el término SI (*super intelligence*). Para este proyecto se propone una IA que explique evidencia citada y un ranking reproducible.

La pregunta que debería poder contestar el usuario es **¿qué evidencia de NASA ayuda a entender este escenario, bajo qué condiciones se obtuvo y qué información falta?** El producto apoya la exploración de evidencia sobre prevención, detección y supresión en naves, estaciones, hábitats lunares o marcianos y vehículos presurizados. También puede facilitar la extracción de datos para investigación, modelos de inflamabilidad y tecnologías de seguridad. El diseño operativo de sistemas contra incendios y la combustión interna de motores cohete quedan fuera del alcance propuesto.

La audiencia incluye ingenieros y planificadores de misiones, investigadores de combustión, docentes y estudiantes. Si la entrega corresponde al hackathon, el [calendario oficial](https://www.spaceappschallenge.org/2026/) indica el **domingo 15 de noviembre de 2026 a las 11:59 p. m., hora local**. Confirmar el evento local, el formato de la demo y las condiciones de entrega en la [guía oficial de recursos](https://www.spaceappschallenge.org/resources/).

## Casos de uso, temas y escenarios

**El dashboard puede cubrir varios casos de uso y temas.** La priorización de un recorrido principal facilita construir y presentar la primera demo.

| Concepto | Aplicación al proyecto |
| --- | --- |
| Caso de uso | Buscar y filtrar, abrir una ficha con fuentes, comparar estudios, ordenar evidencia para un escenario, pedir una explicación a la IA o exportar datos. |
| Tema científico | Ignición, propagación en sólidos, humo y aerosoles, extinción, combustión de gotas o llamas gaseosas. |
| Escenario | Una cabina con ventilación en microgravedad, un hábitat lunar, un hábitat marciano o una referencia terrestre. Cada escenario indica las condiciones que se conocen y las que quedan abiertas. |

**Recorrido principal propuesto.** Una persona consulta la propagación de llama en un sólido bajo ventilación forzada en una cabina. Filtra investigaciones, abre BASS-II, compara con un segundo estudio y consulta qué evidencia se aproxima a su escenario. La explicación cita las fuentes y muestra las diferencias que condicionan la aplicación del resultado.

**Recorridos adicionales.** Explorar humo y aerosoles con SAME-R. Consultar un escenario lunar para demostrar cómo se identifican analogías y vacíos de información. Extender a gotas, gas y aplicaciones terrestres conforme haya evidencia curada.

## Contexto científico para el equipo

En microgravedad disminuye el transporte por flotabilidad respecto a la Tierra. La difusión y la ventilación forzada pueden adquirir mayor peso. Una llama puede adoptar una forma aproximadamente esférica en ciertas condiciones. Para interpretar resultados, registrar la concentración de oxígeno, la presión absoluta, la ventilación y dirección del flujo, el régimen de gravedad, el material o combustible, el espesor y la geometría. Registrar también el aparato, el sensor, la escala y el método. [Panorama de combustión en microgravedad de NASA](https://svs.gsfc.nasa.gov/31394/)

La fracción de oxígeno y la presión total son variables distintas. Registrar si la composición corresponde al ambiente de la cámara o a una corriente del quemador. Por ejemplo, el valor de hasta 85 % de oxígeno citado para CFI-G corresponde a una mezcla inyectada por el quemador de una configuración invertida. [Antecedentes del reto](https://hackathlone.com/challenges/flame-in-freefall) · [Informe diario NASA sobre CFI-G](https://www.nasa.gov/blogs/stationreport/2021/08/20/iss-daily-summary-report-8-20-2021/)

| Escenario o referencia | Cómo usarlo |
| --- | --- |
| Cabina ventilada en microgravedad | Escenario principal propuesto. Elegir material, tipo de flujo y, si se conocen, presión y oxígeno. Representar la microgravedad como régimen experimental y dejar la aceleración numérica vacía si falta una medición. |
| Hábitat o rover lunar presurizado | La gravedad lunar es aproximadamente 1/6 de la terrestre. Los valores de 30 % o más de O₂ y hasta alrededor de 10,2 psia aparecen como contexto del reto. La combinación 32 % a 10,2 psia de las notas es un ejemplo hipotético. NASA también documenta una atmósfera de exploración propuesta de 8,2 psia y 34 % de O₂ para futuras misiones. Tratar cada combinación como escenario identificado con fuente o como entrada del usuario. |
| Traje EVA | 4,3 psia y 100 % de O₂ aparecen como referencia para el traje considerado por NASA. La presión se refiere al interior del traje. Un caso EVA necesita contexto y estudios pertinentes propios. |
| Tierra | Puede servir como referencia nominal aproximadamente 1 g, 14,7 psia al nivel del mar y 21 % de O₂. Para comparar ensayos, utilizar las condiciones reportadas en cada fuente. |
| Hábitat marciano presurizado | Ampliación propuesta. Permitir entradas configurables y mostrar la cobertura de evidencia. Mantener explícitos el entorno gravitatorio y la atmósfera interior. |

Fuentes de referencia: [antecedentes del reto](https://hackathlone.com/challenges/flame-in-freefall), [NASA sobre atmósferas de exploración](https://ntrs.nasa.gov/citations/20230015380) y [FM² de NASA](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-of-materials-on-the-moon-fm2/).

El material del reto señala un vacío de datos de combustión en gravedad parcial dentro de PSI. Registrar la cobertura **del catálogo consultado** y revisar PSI antes de ampliar esa afirmación. El informe de LUCI documenta ensayos con gravedad lunar simulada mediante rotación en un cohete sonda. FM² se diseñó para hacer mediciones en la superficie lunar. E-FIELD Flames aplicó campos eléctricos a llamas de difusión y sirve como analogía limitada a los efectos estudiados. Distinguir medición in situ, ensayo con gravedad parcial simulada, analogía física, modelo e inferencia. La interpolación entre Tierra y microgravedad requiere un modelo respaldado y una validación específica. [LUCI en NTRS](https://ntrs.nasa.gov/citations/20250010653) · [FM²](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-of-materials-on-the-moon-fm2/) · [E-FIELD Flames](https://science.nasa.gov/biological-physical/investigations/e-field-flames/)

## Investigaciones y fuentes iniciales

La ficha de un estudio puede incorporarse al catálogo cuando sus metadatos estén corroborados. Las filas de ensayos y las métricas necesitan una localización verificable en el archivo o publicación original.

| Estudio o familia | Tema y uso propuesto | Punto de partida |
| --- | --- | --- |
| **BASS-II (PSI-25)** | Estudio piloto. Combustión, propagación y extinción de sólidos en microgravedad con ventilación. El reporte incluye ensayos de PMMA con flujo opuesto en MSG. | [Ficha PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) · [Informe NASA/TM-20210011385](https://ntrs.nasa.gov/citations/20210011385), sección 2.2.3 para el montaje de esa serie |
| **BASS** | Candidato para comparar con BASS-II. Revisar geometría, combustible, dirección de flujo y variable medida antes de cruzar resultados. | [Publicación NASA NTRS 20140011099](https://ntrs.nasa.gov/citations/20140011099) |
| **Saffire I–III** | Propagación en sólidos y demostraciones de incendio en una nave de carga Cygnus. Puede aportar evidencia a otra escala y servir para mostrar diferencias de montaje. | [Índice PSI de NASA](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/) · [Resumen técnico en NTRS](https://ntrs.nasa.gov/citations/20210017780) |
| **SoFIE** | Ignición, crecimiento y extinción de combustibles sólidos. Elegir una investigación concreta y verificar su disponibilidad y compatibilidad antes de poblar mediciones. | [NASA Science: SoFIE](https://science.nasa.gov/biological-physical/investigations/sofie/) |
| **SAME / SAME-R (PSI-101 para SAME-R)** | Humo, características de partículas y transporte de aerosoles relevantes para detección. SAME-R es el segundo piloto propuesto. | [Ficha PSI-101](https://psi.nasa.gov/physci/repo/data/investigations/PSI-101) · [Resultados de morfología y tamaño de partículas](https://ntrs.nasa.gov/citations/20130000422) |
| **FLEX / FLEX-2** | Combustión y extinción de gotas. Revisar por separado qué combustibles, configuraciones y diluyentes corresponden a cada estudio. | [Índice PSI](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/) · [Ficha NASA de FLEX-2](https://www.nasa.gov/wp-content/uploads/2025/07/flame-extinguishment-experiment-flex.pdf) |
| **ACME, CFI y CFI-G** | ACME estudia llamas gaseosas en CIR. CFI-G estudia llamas frías de gases. CFI de gotas se asocia con FLEX y el equipo MDCA. BRE emplea gases para estudiar cuestiones de inflamabilidad. E-FIELD estudia efectos de campos eléctricos. | [Descripción y recursos del reto](https://hackathlone.com/challenges/flame-in-freefall) · [Índice PSI](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/) |
| **SPICE, SLICE y DAFT / DAFT-2** | SPICE aporta contexto sobre hollín en llamas de coflujo. SLICE estudia estructura y desprendimiento de llamas. DAFT y DAFT-2 aportan contexto instrumental sobre polvo y aerosoles frente a los estudios SAME. | [Índice PSI](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/) · [Descripción y recursos del reto](https://hackathlone.com/challenges/flame-in-freefall) |
| **LUCI, FM² y E-FIELD Flames** | Referencias para la vista lunar. Indicar el régimen y el tipo de evidencia que cada fuente aporta. | [LUCI](https://ntrs.nasa.gov/citations/20250010653) · [FM²](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-of-materials-on-the-moon-fm2/) · [E-FIELD Flames](https://science.nasa.gov/biological-physical/investigations/e-field-flames/) |

**Hardware.** CIR es el *Combustion Integrated Rack* de la Estación Espacial Internacional (EEI o ISS). MDCA es el aparato de combustión de gotas instalado en CIR. MSG es el *Microgravity Science Glovebox*. BASS, BASS-II, SPICE y SLICE usaron un conducto modular de ventilación en MSG. Una instalación o un conducto compartido aporta contexto, y la comparabilidad depende también del fenómeno, el material, el método y las condiciones. [Antecedentes y recursos del reto](https://hackathlone.com/challenges/flame-in-freefall)

**Aplicaciones terrestres opcionales.** Se puede documentar el uso de niebla de agua fina en entornos confinados, detectores que distinguen partículas de combustión y polvo, y equipos para bomberos. Verificar el origen y la aplicación de cada tecnología con la fuente correspondiente. [Equipo de respuesta en entornos confinados](https://ntrs.nasa.gov/citations/20110015892) · [Detector en NASA Spinoff](https://spinoff.nasa.gov/node/9407) · [Recursos del reto](https://hackathlone.com/challenges/flame-in-freefall)

## Hoja de ruta

| Fase | Trabajo | Entregable verificable |
| --- | --- | --- |
| **1. Delimitar la investigación** | Definir la pregunta de la demo, el fenómeno principal y las condiciones necesarias para interpretar un resultado. | Escenario de cabina ventilada y lista de variables prioritarias. |
| **2. Inventariar las fuentes** | Empezar por BASS-II y SAME-R. Buscar un segundo estudio de sólidos. Registrar ID PSI, DOI o ID NTRS, archivos, tipo de evidencia, variables y páginas, figuras o tablas. | Fichas piloto y una fuente original localizada para cada una. |
| **3. Curar el dataset** | Extraer metadatos y ensayos accesibles, validar unidades y conservar localizadores. Documentar faltantes y diferencias de métodos. | Dataset pequeño que permita reproducir cada valor y conectarlo con su estudio. |
| **4. Construir el dashboard** | Implementar catálogo, filtros, ficha y comparación lado a lado. Incorporar gráficos cuando existan mediciones compatibles. | Flujo de búsqueda, ficha y comparación comprobado con datos reales. |
| **5. Integrar ranking e IA** | Ordenar estudios según el escenario, mostrar la razón del orden y generar explicaciones con evidencia recuperada y citada. | Escenario que devuelve estudios ordenados y distingue hallazgos, interpretación y límites. |
| **6. Verificar y preparar la demo** | Probar condiciones comparables y diferencias de montaje, datos ausentes, una consulta lunar y acceso a fuentes. Preparar la entrega si aplica. | Demo accesible y guion que recorre pregunta, estudios, evidencia y límites. |

La meta propuesta para el hackathon es **3 o 4 fichas verificadas**. Empezar con BASS-II, otro estudio de sólidos con datos utilizables y SAME-R. Añadir una cuarta ficha si mejora un recorrido y tiene respaldo. La primera tarea de investigación es localizar un hallazgo de BASS-II en una tabla, figura o sección del reporte de NASA, junto con el método, la unidad y las condiciones relevantes.

## Requisitos e historias de usuario

| ID | Historia o función | Criterio de aceptación | Prioridad propuesta |
| --- | --- | --- | --- |
| RF-01 / US-01 | Como ingeniera o estudiante, quiero buscar y filtrar investigaciones por tema, combustible o material y gravedad. | La lista responde a filtros combinados. Los filtros de O₂, presión, flujo o hardware se agregan según cobertura. Los valores desconocidos quedan identificados, y cero sigue siendo un valor válido. | MVP básico |
| RF-02 / US-02 | Como investigador, quiero abrir la ficha de un estudio para entender qué se ensayó y consultar el original. | La ficha muestra objetivo, muestra, geometría, equipo, condiciones, variables controladas y medidas, hallazgos, límites y enlaces. Cada dato clave lleva a su fuente. | MVP |
| RF-03 / US-03 | Como estudiante o profesional, quiero una explicación de la evidencia en lenguaje claro. | La IA devuelve objetivo, hallazgos, implicaciones y límites. Las afirmaciones concretas están citadas y la interfaz identifica observaciones, resultados de modelos e interpretaciones. | MVP |
| RF-04 / US-04 | Como investigador, quiero comparar dos estudios para ver semejanzas, diferencias y resultados. | La tabla muestra ambas condiciones y unidades. El gráfico compartido solo aparece para la misma magnitud y condiciones interpretables. Una diferencia importante tiene una advertencia específica. | MVP |
| RF-05 / US-05 | Como planificador, quiero consultar un escenario y saber qué estudios son relevantes y dónde hay vacíos. | El orden explica coincidencias, diferencias y campos desconocidos. La consulta lunar distingue datos directos, ensayos simulados, analogías y modelos que estén disponibles en el catálogo. | MVP |
| RF-06 | Quiero navegar por comportamiento del fuego, inflamabilidad de sólidos, detección de humo y combustión de líquidos. | Los temas se alimentan del catálogo curado. Se habilitan a medida que haya fichas y evidencia. | Sólidos y humo primero. Ampliar después |
| RF-07 | Como investigador, quiero exportar datos para reutilizarlos o evaluar su utilidad en un modelo. | CSV o JSON conserva IDs, valores, unidades, método, procedencia y tipo de evidencia. El archivo indica qué filtros se aplicaron. | Ampliación |
| US-06 | Como docente o evaluador, quiero consultar aplicaciones terrestres de la investigación. | Cada caso muestra la tecnología, la aplicación y una fuente verificable. | Ampliación |

| Requisito no funcional | Criterio |
| --- | --- |
| RNF-01. Trazabilidad | Cada cifra, observación y resumen factual puede rastrearse hasta el estudio y su localizador. |
| RNF-02. Transparencia científica | Mostrar campos faltantes, alcance del método y naturaleza de cada evidencia. Las inferencias incluyen sus supuestos y límites. |
| RNF-03. Usabilidad y accesibilidad | Mostrar unidades junto a los valores y etiquetas claras en filtros y alertas. La información esencial de los gráficos también está disponible como texto o tabla. |
| RNF-04. Rendimiento | Filtros y comparación responden sin recargar toda la página. Un dataset versionado evita consultar PSI en cada interacción. |

## Modelo de datos propuesto

Empezar con JSON versionado o CSV relacional. Los nombres de archivos orientan la implementación y todavía son propuestas.

| Archivo | Una fila representa | Campos principales |
| --- | --- | --- |
| `investigations_master.json` | Una investigación | `investigation_id`, `psi_id`, título, familia, objetivo, temas, combustibles y geometrías, plataforma, aparato, entorno, sensores, variables controladas y medidas, hallazgos, limitaciones y fuentes. |
| `experimental_runs.json` | Un ensayo o una condición dentro de una serie identificable | `run_id`, `investigation_id`, material y geometría, instalación y método, presión absoluta, oxígeno y corriente a la que pertenece, flujo y dirección, régimen de gravedad, mediciones, resultados y fuentes. |
| `operational_scenarios.json` | Un escenario de referencia o una plantilla para entradas del usuario | `scenario_id`, entorno, fenómeno, material, gravedad, O₂, presión, flujo, procedencia y clasificación como referencia documentada o hipótesis. |

Cada medición puede guardar `metric`, `value`, `unit`, `method`, incertidumbre cuando exista y `source` con URL, ID o DOI, nombre del archivo y página, figura, tabla o fila. Conservar valor y unidad originales al normalizar y mantener el método de conversión. Diferenciar condiciones fijadas por el diseño, mediciones directas, valores calculados y resultados de simulación. Documentar cuando un valor se extraiga de una figura, con su precisión o incertidumbre.

Usar `null` para un valor desconocido y mostrar **Sin dato**. Cuando se conozca el motivo, registrar si la fuente omitió el dato, la variable no aplicaba o la extracción está pendiente. No convertir microgravedad a un cero medido por defecto ni usar una misma métrica para hollín, tamaño de aerosol y señal del sensor. Los nombres, cifras e IDs de ejemplo de las notas previas, incluido `RUN-CFIG-015`, representan borradores de esquema. Mantenerlos fuera del dataset científico hasta rastrearlos a una fuente.

**Comparación.** Verificar la magnitud, la unidad, el método, el estado y la geometría del combustible, la atmósfera, el régimen gravitatorio, el flujo, el montaje y la escala. Identificar qué variable cambia deliberadamente. Usar la tabla para mostrar diferencias; una tasa de propagación de sólidos en mm/s y una constante de combustión de gotas expresada en mm²/s deben tener representaciones propias. Registrar denominadores y condiciones de medición en cualquier comparación cuantitativa.

## Ranking y respuestas de IA

1. Representar el escenario con campos explícitos. Priorizar el fenómeno consultado, el tipo de combustible o material y el régimen de gravedad. Incorporar diferencias de O₂, presión, flujo y geometría según los campos disponibles y la comparabilidad.
2. Definir reglas deterministas y visibles. Mostrar qué coincide, qué difiere y qué se desconoce. Documentar los criterios de orden y el desempate si se implementa un puntaje. El resultado expresa **relevancia de la evidencia para la consulta**. Los empates o los datos insuficientes deben quedar visibles.
3. Recuperar fichas y extractos con sus fuentes. Dar a la IA ese material como contexto y hacer que cite los identificadores y localizadores. Presentar sus explicaciones como interpretación. Revisar explícitamente las cifras, las condiciones, el tipo de evidencia y la validez de los enlaces.
4. Ante una consulta sin evidencia suficiente, indicar la cobertura del catálogo y los campos faltantes. Si se muestran estudios análogos, explicar qué aspecto se parece y qué limita su aplicación. El producto se plantea como explorador científico. Evitar conclusiones operativas o puntuaciones de riesgo sin un método validado.

## Verificación de la demo

- Buscar BASS-II, abrir la ficha y rastrear una observación hasta su publicación.
- Comparar dos estudios de sólidos con evidencia comparable o mostrar las diferencias que impiden interpretar una métrica conjunta.
- Comparar BASS-II y SAME-R para comprobar que la tabla explica la diferencia de fenómeno y medición.
- Consultar un escenario lunar y verificar que se pueda distinguir una analogía de una medición en las condiciones de interés.
- Probar una búsqueda vacía y una ficha con variables desconocidas. Verificar que la IA reconozca una pregunta sin respaldo en el catálogo.
- Revisar unidades, links y acceso público de la demo antes de la entrega. En la página del proyecto, describir las fuentes de NASA utilizadas y cómo se empleó la IA conforme a la guía del evento.

## Traspaso entre integrantes e IAs

Al comenzar una tarea, lee este archivo y revisa el estado actual de la rama y los archivos relevantes. Indica qué requisito o historia estás desarrollando, qué fuente respalda los datos y qué supuestos quedan abiertos. Si agregas evidencia, registra el localizador y el tipo de evidencia en la misma contribución. Si una decisión del equipo cambia el MVP, el esquema o el ranking, actualiza esta guía junto con el cambio.

**Texto para iniciar otra sesión de IA**

> Estamos construyendo el dashboard de Team Changeme para Flame in Freefall de NASA Space Apps 2026. Lee ANALISIS/CONTEXTO_FLAME_IN_FREEFALL.md y revisa el repositorio antes de modificar archivos. Implementa la tarea asignada con datos trazables a PSI o a publicaciones de NASA. Distingue mediciones, modelos, analogías e interpretaciones. Conserva las unidades y los localizadores, señala los campos desconocidos e indica qué verificaste al terminar.

**Pendientes del equipo**

- Confirmar alcance de la entrega, responsables, herramientas, proveedor de IA y sitio de demostración.
- Elegir el segundo estudio de sólidos después de revisar fuentes y compatibilidad con BASS-II.
- Verificar qué archivos se pueden descargar y reutilizar. Poblar y revisar los primeros ensayos.
- Acordar criterios de orden y un conjunto pequeño de preguntas de prueba.
- Validar las condiciones de cada escenario que se muestre como referencia documentada.

## Referencias de arranque

- [Reto oficial Flame in Freefall](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/)
- [Descripción ampliada y recursos del reto en HackAthlone](https://hackathlone.com/challenges/flame-in-freefall)
- [Video del reto](https://youtu.be/AVuEiKxOpc0)
- [Búsqueda de combustión en NASA PSI](https://psi.nasa.gov/physci/repo/search?q=combustion)
- [Índice de investigaciones PSI por área](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/)
- [Calendario oficial de NASA Space Apps 2026](https://www.spaceappschallenge.org/2026/)
