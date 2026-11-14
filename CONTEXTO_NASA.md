# Contexto de Flame in Freefall

Consulta realizada el 14 de noviembre de 2026.

Entrega posterior v0.3: el usuario pidió integrar todos los datos y excluir documentos. Se integraron fuentes ya descargadas en `data/integrated/nasa_integrado.duckdb`, con maestro de 420.421 registros/145 columnas y vista de análisis de 330.479 registros que excluye 89.942 eventos sin reloj presente. El detalle contiene 11.628.452 versiones de valores y 13.390.304 relaciones con celdas de origen; se consolidaron 1.761.852 coincidencias exactas. Hay 307 registros canónicos de condiciones y 556 puntos de calibración. Se preservan las 225.300 filas calibradas completas. No confundir tipos de registros, dominios de procesamiento ni relojes. Los conflictos no se promedian. Paquetes nuevos `NASA_DATOS_INTEGRADOS_v0.3.zip` y `NASA_DATOS_DETALLADOS_v0.3.zip` contienen solo tablas y metadatos de procedencia, sin documentos ni índices de imágenes. Guía: `DATOS_INTEGRADOS_GUIA.md`. Pasaron 18 pruebas.

Actualización de datos: el usuario pidió un dataset grande y después todo lo recuperable de SAFFIRE y BASS, manteniendo la exclusión audiovisual. Se descargaron los CSV originales de cinco investigaciones y se generó un catálogo de 263 registros, pero el usuario aclaró que necesitaba muchas mediciones. La entrega ampliada está descrita en `DATASET_AMPLIADO_README.md`: 225.300 registros temporales calibrados de 13 archivos de SAFFIRE-I/II/III, además de matrices BASS/BASS-II y documentación. No confundir esos instantes correlacionados con ensayos independientes. Archivos en `data/expanded_processed`; fuentes e incidencias en `data/expanded_raw/manifest.json`. Se recuperaron 105 archivos (~484 MB); cinco documentos complementarios devolvieron 404. Los TXT de BASS son metadatos fotográficos, no sensores. Las matrices, ReadMe y SRD de BASS-II antes inaccesibles ya fueron descargadas. Los archivos audiovisuales y ZIP no clasificados siguen excluidos.

Actualización: se completó una profundización documental externa, excluyendo audiovisuales. El análisis, hallazgos, localizadores y registro preciso de cobertura están en [INVESTIGACION_EXTERNA_NASA.md](INVESTIGACION_EXTERNA_NASA.md). Ese registro prevalece sobre las descripciones de lectura inicial que siguen. El informe SAME ya se descargó correctamente; también se incorporaron el informe FLEX de 314 páginas y una evaluación científica de detectores publicada en 2018. Persisten archivos técnicos de PSI sin leer y no se auditó cada ensayo de FLEX.

## Alcance acordado con el usuario

Es un proyecto de hackathon. El usuario aclaró expresamente que `Resumen_Flame_in_Freefall.pdf` es el documento instructivo de los objetivos y entregables. `G1_NASA2026.pdf` y `Recursos_NASA.docx` son material de apoyo y rutas hacia las fuentes. La solicitud actual fue contextualizarse y consultar esas fuentes; todavía no se ha solicitado construir, publicar ni presentar la aplicación.

Archivos originales leídos:

- `C:\Users\inteligencia\Downloads\Resumen_Flame_in_Freefall.pdf`: cuatro páginas, lectura textual y visual.
- `C:\Users\inteligencia\Downloads\G1_NASA2026.pdf`: cuatro páginas, lectura textual y visual, incluidos enlaces de anotaciones y una tabla de MVP incrustada como imagen.
- `C:\Users\inteligencia\Downloads\Recursos_NASA.docx`: texto y relaciones externas de los hipervínculos.

## Objetivos del entregable

Un dashboard web interactivo con IA que resuma, clasifique por relevancia e interprete investigaciones de combustión en microgravedad para apoyar la seguridad contra incendios en entornos habitables espaciales.

Debe ayudar a identificar investigaciones relevantes, localizar datos que sirvan para modelos predictivos y destacar evidencia útil para controles y equipos de seguridad. Los usuarios potenciales incluyen estudiantes, docentes, investigadores e ingenieros.

Las capacidades descritas en el resumen incluyen búsqueda y filtros, resúmenes con IA, comparación contextualizada, ranking explicado, visualizaciones, identificación o extracción de datos y enlaces a las fuentes. Cada investigación requiere objetivo, combustible/material, geometría, condiciones, variables, sensores, resultados, limitaciones y relaciones con otros estudios.

Criterios centrales: trazabilidad; unidades y condiciones explícitas; distinción entre medición, interpretación y predicción; advertencias sobre datos faltantes y comparaciones inválidas; lenguaje accesible con rigor técnico. El foco es prevención, detección y supresión en naves, estaciones, hábitats y vehículos presurizados. Cohetes y propelentes quedan generalmente fuera del alcance.

La tabla incrustada en G1 propone inicialmente SoFIE, BASS/BASS-II, SAME y FLEX/FLEX-2. SPICE, FLARE y FM2 aparecen como ampliaciones posteriores. Es una propuesta del material de apoyo, no una decisión adicional confirmada por el usuario.

## Repositorios y datos comprobados

- [PSI búsqueda](https://psi.nasa.gov/physci/repo/search?q=combustion): accesible por navegador. La búsqueda textual mostró 26 coincidencias, incluyendo áreas distintas de Combustion Science. No confundir ese número con el total del área. El intento de marcar el filtro por área no quedó confirmado.
- [BASS-II PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25): ficha, descripción, tabla experimental y publicaciones revisadas. DOI `10.60555/4qc4-de67`, versión 4, actualización de metadatos del 24 de noviembre de 2025, licencia CC0-1.0. La tabla visible indicaba 130 filas. Incluye material, muestra, prueba, lecturas de flujo, oxígeno inicial/final, CO y CO2. El repositorio completo anunciaba 255.77 GB; no se descargó íntegro.
- [FLEX PSI-69](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69): ficha, descripción, tabla experimental y publicaciones revisadas. DOI `10.60555/mbq8-0451`, versión 5, actualización del 6 de junio de 2025, licencia CC0-1.0. La tabla visible indicaba 275 filas. Incluye combustible, presión, composición ambiental, diámetro de gota, diámetro de extinción visible, tasa de combustión, duración y motivo de terminación. El repositorio completo anunciaba 860.39 GB; no se descargó íntegro. Verificar unidades y subíndices en el archivo original antes de importar: algunos encabezados se pierden en la representación accesible.
- [NASA Open Data](https://data.nasa.gov/): página general consultada. Es un catálogo de metadatos con enlaces a archivos alojados en otros sistemas. La antigua URL de búsqueda incluida en G1 no fue legible mediante la consulta web; no se verificó una selección de resultados de esa búsqueda.
- [NTRS](https://ntrs.nasa.gov/): se consultaron registros y se descargaron siete publicaciones enlazadas para lectura local.

Identificadores adicionales observados en los resultados de PSI: BASS PSI-26; FLEX-2 PSI-68; SAME PSI-102; SAME-R PSI-101; Saffire I/II/III PSI-98/99/100; SPICE PSI-107; SLICE PSI-106; CFI PSI-39; ACME CFI-G PSI-159; BRE PSI-20; E-FIELD PSI-22. Esas fichas adicionales no fueron todas revisadas individualmente.

## Fuentes científicas consultadas

- [NASA Combustion Science](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/): marco científico y familias de investigaciones.
- [Guía de investigadores](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/) y [PDF de 56 páginas](https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf): descargado y extraído; revisadas secciones sobre fundamentos, gotas, gases, sólidos, detección/supresión, lecciones aprendidas e instalaciones. Edición de 2015, no catálogo del estado actual.
- [BASS-II presentación](https://ntrs.nasa.gov/api/citations/20160000593/downloads/20160000593.pdf): 21 páginas, texto leído. Variables, geometrías, extinción por bajo y alto flujo y resultados específicos de PMMA.
- [BASS-II informe NASA/TM-20210011385](https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf): 144 páginas, descargado y extraído; revisados resumen, descripción experimental, conclusiones generales y secciones seleccionadas. No se auditó cada tabla ni se reprodujeron sus cálculos.
- [SAME informe final NASA/NIST](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=904707): PDF de 61 páginas. La descarga inicial recibió HTTP 403; un acceso posterior permitió descargarlo y leer su cuerpo científico y apéndices sustantivos. Véanse los hallazgos y discrepancias de tabla/prosa en la investigación externa.
- [SAME-2 artículo](https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf): 13 páginas, descargado y extraído; revisados objetivos, metodología, resultados seleccionados y conclusiones. Materiales sobrecalentados por debajo de ignición, distribución de tamaños, envejecimiento y respuesta de detectores.
- [Burning Questions in Gravity-Dependent Combustion Science](https://ntrs.nasa.gov/api/citations/20130004397/downloads/20130004397.pdf): presentación de 24 páginas de 2012, texto leído. Está enlazada bajo SAME en G1, pero trata el programa de combustión en general.
- [SoFIE](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/solid-fuel-ignition-and-extinction-sofie/) y [SoFIE-MIST](https://science.nasa.gov/biological-physical/investigations/sofie-mist/): páginas consultadas; MIST considera flujo, oxígeno, presión y radiación externa para estudiar ignición y extinción de PMMA.
- [FLARE](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-limits-at-reduced-g-experiment-flare/): correlación entre límites de inflamabilidad terrestres y de microgravedad; la página conserva planes históricos, que no prueban el estado actual.
- [FM2](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-of-materials-on-the-moon-fm2/) y [póster de 2024](https://ntrs.nasa.gov/citations/20240015307): página, registro y texto del póster revisados. Distinguir pruebas terrestres que simulan gravedad lunar, objetivos futuros y datos efectivamente obtenidos en la superficie lunar.
- [SPICE ficha](https://www.nasa.gov/wp-content/uploads/2025/07/smoke-point-in-co-flow-experiment-spice.pdf): dos páginas leídas; reporta 250 pruebas y más de 70 puntos de humo. Relaciona combustible, flujo, hollín y radiación.
- [Spherical Flames](https://svs.gsfc.nasa.gov/11640): explicación NASA SVS de FLEX-2; texto consultado, sin afirmar haber visto el video completo.
- [Imagen BASS-II](https://commons.wikimedia.org/wiki/File:ISS-46_BASS-II_flame_test_with_reduced_oxygen_partial_pressure.jpg): ficha consultada como recurso visual, no como base principal para conclusiones científicas.

## Historia, aplicaciones y descripción del reto

Consultadas las páginas enlazadas de [Apolo 1](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1), [Apolo 13](https://sma.nasa.gov/sma-disciplines/accllp/apollo-13), [incendio de Mir](https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/), [tanques de aire](https://spinoff.nasa.gov/node/9582), [detector de incendios](https://spinoff.nasa.gov/node/9407) e [indumentaria de bomberos](https://spinoff.nasa.gov/node/9918). Son contexto histórico y de transferencia tecnológica, no datasets experimentales comparables.

La URL visible de Apolo 1 en el DOCX estaba concatenada con YouTube. Su hipervínculo interno contenía la dirección correcta, que se utilizó.

Se consultó la [descripción de Flame in Freefall en HackAthlone](https://hackathlone.com/challenges/flame-in-freefall). Es una página del evento fuera del dominio NASA; se utiliza como contexto del desafío y se conserva el resumen del usuario como guía de entregables.

Se recuperó y leyó la transcripción del [video NASA ScienceCasts de 2018](https://www.youtube.com/watch?v=W1oXykoz9zg). Las cifras energéticas y cronologías que menciona deben atribuirse a ese contexto histórico. Se abrió el [video del desafío](https://www.youtube.com/watch?v=AVuEiKxOpc0), pero no ofreció transcripción accesible: no afirmar que se revisó su contenido audiovisual completo.

## Matices que deben conservarse

1. Microgravedad no significa que desaparezca la gravedad: se reducen los efectos aparentes y la convección por flotabilidad durante la caída libre.
2. No todas las llamas son esféricas. La geometría y la ventilación forzada cambian su estructura.
3. La seguridad depende conjuntamente de material, geometría, oxígeno, presión, flujo y calentamiento. La concentración de oxígeno sola no basta.
4. SAME caracteriza aerosoles de materiales sobrecalentados para informar el diseño de detectores; no se reduce a comprobar que un P-Trak funciona.
5. No confundir extinción de la llama visible con cese de toda reacción: FLEX y CFI aportan evidencia sobre llamas frías.
6. La dependencia con gravedad y ventilación puede ser no monótona. Los resultados de 0g y 1g no garantizan límites conservadores para gravedad lunar o marciana.
7. La descripción del reto declara que no hay datos de combustión de gravedad parcial disponibles en PSI. No se verificó exhaustivamente todo el catálogo para certificar su estado actual. FM2 no debe presentarse como un dataset lunar ya obtenido basándose solamente en páginas de objetivos o planes.
8. BASS-II: el informe de 2021 menciona 126 ensayos; la tabla actual de PSI mostraba 130 filas. No atribuir la diferencia a un motivo sin inspeccionar los registros.
9. Compartir CIR, MSG o un conducto experimental no hace equivalentes dos estudios.
10. Para el dashboard, conviene conservar identificador PSI, DOI, versión, fecha de consulta, fuente y localizador de la evidencia. Es una conclusión de trabajo para cumplir la trazabilidad solicitada, no una implementación ya realizada.

## Material de trabajo local

`tmp/contexto_nasa/` contiene extracciones de texto, siete PDFs científicos descargados y vistas de las páginas de los PDFs originales. No contiene una copia integral de los datos brutos de PSI. Esta nota es una contextualización inicial con revisión de secciones científicas relevantes, no una revisión sistemática exhaustiva ni validación de un modelo predictivo.
