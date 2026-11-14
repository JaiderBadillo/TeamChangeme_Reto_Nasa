# Flame in Freefall: investigación de las fuentes externas

Fecha de revisión: 14 de noviembre de 2026. Alcance: documentación escrita, publicaciones, tablas y fichas de repositorios. Se excluyeron audio, videos y sus transcripciones de esta profundización. Las figuras estáticas de documentos científicos sí se usaron para comprobar tablas.

El documento del usuario `Resumen_Flame_in_Freefall.pdf` sigue definiendo los objetivos de la hackathon. Las fuentes externas aportan evidencia científica; sus planes, recomendaciones y procedimientos experimentales no constituyen nuevas instrucciones del usuario.

## 1. Qué cambia después de profundizar

La evidencia permite organizar el proyecto alrededor de tres preguntas diferentes: cómo se propaga o extingue una llama, cómo se forma y detecta el humo antes de la ignición, y qué datos permiten comparar condiciones. No conviene convertir todas las investigaciones en una única clasificación de “peligrosidad”.

- **BASS-II** aporta condiciones y límites de propagación en sólidos; el resultado depende de geometría, flujo y oxígeno.
- **SAME/SAME-R** aporta aerosoles de materiales sobrecalentados y respuesta instrumental. Humo, llama y detección son resultados distintos.
- **FLEX** aporta combustión de gotas y magnitudes derivadas; permite estudiar mecanismos de extinción, con restricciones instrumentales importantes.
- **SoFIE, FLARE y FM2** amplían las preguntas sobre ignición, radiación y gravedad. Una página de objetivos no demuestra que exista un conjunto público de resultados.

Las recomendaciones para el dashboard que siguen son inferencias de esta revisión, no funcionalidades ya construidas ni requisitos añadidos al resumen de la hackathon.

## 2. BASS y BASS-II: propagación y límites de inflamabilidad

Fuentes: [informe NASA/TM-20210011385](https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf), [presentación](https://ntrs.nasa.gov/api/citations/20160000593/downloads/20160000593.pdf) y [PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25). El informe tiene 144 páginas PDF; sus páginas impresas presentan un desfase de ocho páginas.

### Interpretación física

El flujo tiene efectos contrapuestos: aporta oxidante y favorece el transporte, pero también puede aumentar pérdidas y provocar desprendimiento de la llama. A velocidades bajas puede haber extinción por enfriamiento; a velocidades altas, por blowoff. Entre ambos extremos puede persistir la combustión. Por tanto, una instrucción universal como “más ventilación siempre reduce el riesgo” no se desprende de estos ensayos.

El informe estudia por separado láminas delgadas, barras y tejidos, además de configuraciones de flujo opuesto y concurrente. Sus fronteras experimentales no deben mezclarse en una curva única sin conservar esas diferencias. Un ensayo también puede contener varios cambios de flujo y una muestra puede reutilizarse: muestra, ensayo y condición no son equivalentes.

En las barras de PMMA con flujo concurrente, la frontera de inflamabilidad se describe mediante un ajuste empírico y presenta una región estocástica. El mínimo aproximado de 13,5 % de O₂ corresponde a esa configuración y ajuste; no es un umbral universal de seguridad de cabina. La ignición exige condiciones distintas de las necesarias para mantener una llama ya establecida. Véanse capítulos 2–6, especialmente conclusiones del capítulo 6, páginas impresas 89–90.

La desaparición de la llama tampoco garantiza enfriamiento del sólido. El informe describe pirólisis, chorros de vapor y fenómenos de reignición. Conviene conservar las categorías no ignición, extinción por bajo flujo, blowoff, agotamiento del combustible y detención operativa.

### Instrumentación y calidad

- El anemómetro tiene una respuesta del orden de un minuto y resolución de aproximadamente ±0,5 cm/s. La posición del potenciómetro del ventilador requiere calibración; no es una velocidad física por sí sola.
- El radiómetro se utiliza como señal relativa y no está calibrado para convertir sus valores directamente en flujo térmico absoluto.
- Parte del análisis estima el oxígeno entre lecturas iniciales y finales mediante interpolación lineal. Esa trayectoria es un supuesto de análisis, no una medición continua.
- Las estimaciones de liberación de calor a partir de consumo de oxígeno y duración son magnitudes inferidas. No deben rotularse como una señal instantánea medida.

El apéndice A contiene anomalías que comprobé visualmente en el PDF original, no únicamente en la extracción de texto:

| Localizador PDF / tabla | Registro | Valor publicado | Tratamiento propuesto |
|---|---|---|---|
| 112 / A.1, impresa 104 | B2 | O₂ final calibrado 1,6 %, sin lectura final bruta | Marcar revisión; conservar original |
| 115 / A.3, impresa 107 | P22a / P22b | O₂ final calibrado 0,6 % / 39,1 %, con lecturas brutas incompletas | Revisar calibración y ausencia de datos |
| 121 / A.6, impresa 113 | T28a / T28b | O₂ final calibrado 0,9 % / 40,4 %, con lecturas brutas incompletas | No usar automáticamente en ajustes |
| 121 / A.6 | T9 | Fecha 6/24/2018 dentro de la campaña descrita de 2014 | Mantener fecha original y advertencia |

Esos valores son sospechosos por su contexto; esta revisión no demuestra su causa ni autoriza sustituirlos por cifras “corregidas”. También aparecen CO negativo, sobreescala, guiones y datos no disponibles: cada estado necesita representación propia.

El apéndice C documenta incidencias de hardware y el D contiene un análisis de ingeniería previo. Una predicción de comportamiento del equipo y una anomalía observada después son evidencias de naturaleza diferente.

### Relación con PSI

La ficha consultada de PSI-25 mostraba 130 filas, mientras que el informe menciona 126 ensayos. DOI `10.60555/4qc4-de67`, versión 4; actualización de metadatos indicada: 24 de noviembre de 2025. No se resolvió la correspondencia fila por fila. No se debe atribuir la diferencia a duplicados, exclusiones o ampliaciones sin inspeccionarlos.

## 3. SAME y SAME-R: humo y detección temprana

Fuentes: [informe final NASA/NIST, 61 páginas](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=904707), [artículo SAME-2, 13 páginas](https://ntrs.nasa.gov/api/citations/20130000422/downloads/20130000422.pdf) y [evaluación publicada en 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/).

### Qué se mide

Se produce humo por sobrecalentamiento de materiales, en condiciones de pirólisis previas a un incendio con llama. Cambian el material, la temperatura de calentamiento, la velocidad del aire y el envejecimiento del aerosol. Los materiales de las campañas incluyen Kapton, Teflon, silicona, celulosa y Pyrell; DBP aparece como material de referencia en la campaña inicial. Las listas no deben fusionarse fingiendo que todos los materiales participaron en todos los ensayos.

La metodología combina concentración numérica, respuesta de ionización y masa estimada por dispersión óptica para obtener momentos de la distribución. Es esencial distinguir diámetro geométrico medio, diámetro medio por número y diámetro de masa media. Reconstruir una distribución a partir de los momentos incorpora supuestos, como la aproximación lognormal, y depende de calibraciones, densidad y propiedades ópticas. El método no equivale a medir individualmente todas las partículas.

El informe incluye análisis preliminares de diferentes años como apéndices. Son versiones de la misma línea experimental, no replicaciones independientes. También incorpora simulaciones de transporte: sus tiempos y umbrales son resultados de un modelo con condiciones particulares, no mediciones de vuelo de SAME.

### La publicación posterior matiza una generalización importante

El artículo de 2018 compara ensayos terrestres y orbitales equivalentes. Con flujo de 8,1 cm/s obtiene tamaños similares; la diferencia crece cuando el flujo disminuye y aumenta la permanencia del humo cerca de la fuente. No respalda afirmar que todas las partículas espaciales son mayores. Tampoco ambos detectores detectaron todos los humos: Kapton y Teflon fueron particularmente difíciles para el detector óptico estudiado. Son resultados de esos equipos y condiciones históricas, no una evaluación del estado actual de todos los detectores de la ISS. Fuente: secciones 3.1, 3.2 y 4 del [artículo](https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/).

### Límites e inconsistencias

- La ausencia de partículas visibles en ciertas muestras de microscopía no demuestra ausencia de aerosol: componentes volátiles pueden desaparecer en el vacío. Se deben conservar las limitaciones de muestreo y preparación.
- Los ensayos sin flujo presentan pérdidas de humo por el montaje. Sus concentraciones no son comparables directamente con las de flujo nominal sin considerar esas pérdidas.
- Una correlación ajustada con los instrumentos no es por sí sola un clasificador validado con datos independientes. No se encontró base para presentar una precisión predictiva general del sistema.
- En la página PDF 25, impresa 18, del informe final, la tabla da 606 nm para el diámetro de masa media de silicona envejecida; el texto inmediatamente inferior habla de superar 1 μm para esa magnitud. En el párrafo siguiente denomina CMD a 189 nm, que la tabla asigna a la media geométrica. Comprobé visualmente ambas discrepancias. Hay que conservar el localizador y contrastar la versión de análisis antes de extraer una cifra consolidada.

**Aplicación al proyecto:** las fichas de detección necesitan material, régimen de generación, envejecimiento, transporte, principio del detector, señal/umbral y limitaciones. “Tamaño de humo” sin definir la estadística es insuficiente.

## 4. FLEX: gotas, extinción y variables derivadas

Fuentes: [NASA/TP-2015-216046](https://ntrs.nasa.gov/citations/20150023456), [PDF de 314 páginas](https://ntrs.nasa.gov/api/citations/20150023456/downloads/20150023456.pdf) y [PSI-69](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69).

El informe publica métodos y datos de gotas de metanol y n-heptano; su propósito declarado es archivarlos para análisis posteriores. Leí el cuerpo metodológico y las advertencias, definiciones y ejemplos de los apéndices. No revisé individualmente todos sus gráficos de ensayos.

Los siguientes detalles cambian cómo deben interpretarse los datos; localizadores: páginas impresas 4, 7–9, 16–20 y 29:

| Campo o evento | Interpretación necesaria |
|---|---|
| Burning rate | Constante obtenida de un ajuste de diámetro² frente al tiempo; unidad mm²/s |
| Tiempo cero | Instante de activación del encendedor, no necesariamente ignición autónoma |
| Fin de una curva | Puede corresponder a salida del campo de visión o pérdida de adquisición |
| Diámetro de extinción | En ciertos casos se estima por extrapolación; requiere distinguirlo del valor observado |
| Diámetro de llama | El borde visible y el borde de emisión OH detectado en UV son definiciones distintas |
| Composición ambiental | Se reconstruye considerando llenado y combustiones previas de una atmósfera reutilizada |
| Radiómetros | El informe no publica datos cuantitativos fiables de estos sensores por sensibilidad insuficiente |

El documento también advierte contaminación procedente del recubrimiento de las agujas. Los autores consideran que afecta de forma diferente a las variables y puede explicar ciertas disrupciones. Una etiqueta de anomalía por ensayo es más adecuada que descartar toda la campaña o asumir combustible puro sin advertencia.

La tabla de PSI consultada tenía 275 filas; el resumen del informe anuncia 284 pruebas. No quedó reconciliado ese alcance. El propio informe contiene menciones internas a periodos distintos: para determinar cobertura se necesita comprobar identificadores y fechas, además del título. DOI del repositorio: `10.60555/mbq8-0451`, versión 5, metadatos actualizados el 6 de junio de 2025.

**Aplicación al proyecto:** FLEX permite mostrar curvas y resultados derivados ya publicados sin procesar audiovisuales. No deben transferirse sus límites de gotas directamente a tejidos o superficies sólidas de cabina.

## 5. SoFIE, FLARE, FM2 y SPICE

| Investigación y fuente | Aporte documental | Límite de lo comprobado |
|---|---|---|
| [SoFIE](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/solid-fuel-ignition-and-extinction-sofie/) y [MIST](https://science.nasa.gov/biological-physical/investigations/sofie-mist/) | Ignición/extinción de sólidos; influencia de flujo, O₂, presión y radiación externa | La familia reúne estudios distintos. No se recuperó un dataset público de MIST durante esta revisión |
| [FLARE](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-limits-at-reduced-g-experiment-flare/) | Comparación de límites de inflamabilidad terrestres y en gravedad reducida | La página conserva planes históricos; no acredita ejecución actual ni una norma adoptada |
| [FM2](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-of-materials-on-the-moon-fm2/) y [póster 2024](https://ntrs.nasa.gov/citations/20240015307) | Plantea inflamabilidad en gravedad lunar y pruebas precursoras con PMMA y SIBAL | Ensayos terrestres con gravedad simulada y una propuesta lunar deben etiquetarse por separado. No se recuperaron mediciones realizadas en la Luna |
| [SPICE](https://www.nasa.gov/wp-content/uploads/2025/07/smoke-point-in-co-flow-experiment-spice.pdf) | Formación de hollín en llamas gaseosas con coflujo; la ficha comunica 250 pruebas y más de 70 puntos de humo | Punto de humo no equivale a límite de inflamabilidad ni a número total de pruebas |

La [guía de investigadores de 2015](https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf) y la [presentación de combustión de 2012](https://ntrs.nasa.gov/api/citations/20130004397/downloads/20130004397.pdf) dan el marco común: menos flotabilidad, transporte controlado por difusión y ventilación, efectos de radiación y posibles reacciones de baja luminosidad. Sus fechas se deben mostrar; no son inventarios actualizados de misiones.

## 6. Reglas de comparación derivadas de la lectura

Antes de comparar dos resultados hay que comprobar combustible/composición, geometría y dimensiones, gravedad y plataforma, presión absoluta, fracción de O₂ y diluyente, dirección y velocidad del flujo, calentamiento externo, estado inicial y definición del resultado.

Compartir material no basta. Un límite de ignición de PMMA frío y un límite de extinción de PMMA precalentado responden preguntas diferentes. Tampoco basta compartir instalación: CIR y MSG alojan montajes y campañas diferentes.

Para la extracción propongo conservar:

| Grupo | Campos mínimos |
|---|---|
| Procedencia | Fuente, URL, DOI, versión, fecha de consulta, página/tabla/sección |
| Identidad experimental | Investigación, campaña, muestra, ensayo, intervalo/condición, identificadores alternativos |
| Condiciones | Material, geometría, dimensiones, gravedad, presión, O₂, diluyentes, flujo, radiación, temperatura |
| Resultado | Magnitud, definición, valor, unidad, incertidumbre y método |
| Naturaleza de evidencia | Medida, derivada, simulada, extrapolada, interpretación o plan |
| Calidad | Ausencia, sobreescala, anomalía, censura temporal, revisión necesaria, calibración |

El ranking de relevancia debería explicar qué condiciones coinciden con la consulta y cuáles faltan. No debería sustituirse por una probabilidad de seguridad sin validación. El material leído permite fundamentar un buscador y comparador de evidencia; no demuestra que ya exista un modelo predictivo fiable.

## 7. Registro de lectura y límites pendientes

“Leído” se refiere al alcance indicado en esta tabla. Descargar o extraer texto no equivale a leer, validar datos o reproducir cálculos.

| Fuente externa | Extensión | Cobertura alcanzada |
|---|---:|---|
| BASS-II informe | 144 páginas PDF | Cuerpo científico y apéndices de datos, anomalías e ingeniería revisados; tablas seleccionadas verificadas visualmente. No auditoría de cada cifra ni revisión independiente de toda su bibliografía |
| BASS-II presentación | 21 páginas | Texto completo leído |
| SAME informe final | 61 páginas | Cuerpo científico y apéndices sustantivos leídos; inconsistencia de tabla/prosa verificada visualmente |
| SAME-2 artículo | 13 páginas | Cuerpo científico leído: método, resultados, discusión y conclusiones |
| Evaluación de detectores 2018 | Artículo HTML completo | Texto científico completo leído; referencias identificadas, no lectura recursiva de todos los trabajos citados |
| FLEX informe | 314 páginas PDF | Cuerpo metodológico, discusión, conclusiones, definiciones de tablas y ejemplos de ensayos. Lectura parcial de matrices y apéndice de curvas; no lectura individual de todas las curvas |
| Guía de investigadores | 56 páginas | Secciones científicas sustantivas e instalaciones revisadas; referencias no exploradas exhaustivamente |
| Presentación general de combustión | 24 páginas | Texto completo leído |
| SPICE ficha | 2 páginas | Texto completo leído |
| FM2 póster | 1 página | Texto leído |
| SoFIE, MIST, FLARE y FM2 | Páginas institucionales | Texto leído; se distingue información histórica y objetivos de resultados disponibles |
| PSI-25 y PSI-69 | Fichas y tablas | Metadatos, descripción, tabla visible y documentación localizada; no descarga íntegra de datos brutos |
| PSI-101 SAME-R | Ficha indexada | Información descriptiva recuperada; no descarga de los archivos experimentales |
| Historia y aplicaciones NASA | Páginas enlazadas en Recursos | Consultadas en la contextualización inicial; no investigaciones primarias de incidentes ni datasets experimentales |

**Documentos localizados en PSI-25 que siguen sin leerse:**

- `PSI-25_Science Documents_BASS-II_Test.Matrices.xlsx`
- `PSI-25_Science Documents_BASS-II_ReadMe.docx`
- `PSI-25_Science Documents_BASS-II_SRD.pdf`

Se identificaron y se intentó descargarlos desde el portal, pero no se obtuvo un archivo local utilizable. Esto no implica que sean privados o inexistentes. El nombre de una presentación de requisitos de ingeniería también apareció en el historial del repositorio; su contenido no fue abierto.

**Otros límites:** no se consultaron individualmente todas las fichas de PSI adicionales; no se descargaron las colecciones completas de cientos de GB; no se verificó todo el catálogo para certificar ausencia actual de datos de gravedad parcial; no se siguió cada referencia bibliográfica de cada publicación. Se excluyó todo el contenido audiovisual de este deep dive.

## 8. Archivos y continuidad

Las nueve publicaciones PDF descargadas y sus extracciones están en `C:\team CHANGEME NASA\tmp\contexto_nasa`. Los HTML científicos recuperados, sus textos y las cuatro páginas renderizadas para verificar tablas también están allí. Las copias locales permiten volver a una afirmación concreta sin depender de resúmenes previos.

Esta revisión amplía `CONTEXTO_NASA.md`. Resuelve la descarga anteriormente fallida del informe SAME y profundiza los informes largos; mantiene explícitos los límites que todavía existen. No constituye una revisión sistemática exhaustiva, una certificación de materiales o una validación de un modelo de seguridad.
