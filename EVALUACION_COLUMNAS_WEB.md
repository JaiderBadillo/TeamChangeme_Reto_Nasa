# Evaluación de columnas para Flame in Freefall

Consulta directa de las cinco tablas experimentales de NASA PSI: 14 de noviembre de 2026. Se revisaron los encabezados y las páginas de filas de cada tabla desde el navegador. No se descargaron datasets ni archivos audiovisuales. Esta es una evaluación de las tablas visibles, no de todas las variables presentes en los archivos brutos.

## Decisión de diseño

Las cinco fuentes permiten iniciar un catálogo de investigaciones y ensayos, con búsqueda, filtros y fichas trazables. Para análisis cuantitativo ofrecen coberturas distintas: SAFFIRE-II aporta resultados resumidos de propagación; BASS-II aporta lecturas iniciales y finales de gases; BASS es principalmente un índice de ensayos. No deben importarse como una única tabla plana con todos los valores tratados como números.

| Fuente | Columnas | Filas que anuncia el portal | Lectura de ese recuento |
|---|---:|---:|---|
| [SAFFIRE-I / PSI-98](https://psi.nasa.gov/physci/repo/data/investigations/PSI-98) | 13 | 5 | Dos registros S1/S2, dos auxiliares de flujo y una fila vacía |
| [SAFFIRE-II / PSI-99](https://psi.nasa.gov/physci/repo/data/investigations/PSI-99) | 17 | 16 | Nueve muestras, dos auxiliares, cuatro notas y una fila vacía |
| [SAFFIRE-III / PSI-100](https://psi.nasa.gov/physci/repo/data/investigations/PSI-100) | 9 | 3 | Dos registros S1/S2 y una fila vacía |
| [BASS / PSI-26](https://psi.nasa.gov/physci/repo/data/investigations/PSI-26) | 6 | 123 | Incluye mantenimiento, repeticiones y fila vacía; no equivale a 123 ensayos independientes |
| [BASS-II / PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) | 17 | 130 | Incluye fila vacía, variantes de ensayo y reutilización de muestras |

Los recuentos corresponden a las tablas seleccionadas visibles. No representan todo el contenido de cada repositorio ni el número de observaciones temporales disponibles en sus archivos.

## SAFFIRE-I: condiciones de dos registros y duración

| Columnas originales | Función en el aplicativo | Tratamiento |
|---|---|---|
| Sample Number | Identificar el registro y conectar fuentes | Texto; clave dentro de la investigación |
| Material | Buscar y filtrar materiales | Conservar nombre original y nombre normalizado |
| Sample Thickness (cm), Sample Length (cm), Sample Width (cm) | Describir geometría y comparar escalas | Valor y unidad por separado; revisar coherencia |
| Air Flow (cm/s) | Filtrar velocidad del aire | Número con unidad y definición |
| Percent O2 | Filtrar ambiente | Aceptar intervalo y aproximación |
| Ignition Power (W), Ignition Time (s) | Describir el protocolo de encendido | No confundir tiempo del encendedor con retraso de ignición |
| Burn Time (s) | Mostrar duración reportada | Resultado condicionado por protocolo y causa de terminación |
| Flow Direction | Comparar flujo concurrente y opuesto | Categoría controlada, etiqueta explicada |
| Camera 1, Camera 2 | Trazabilidad hacia recursos | Referencias documentales; no variables científicas |

S1 y S2 muestran 420 y 70 s, respectivamente, con direcciones distintas. El aplicativo puede presentar ese contraste, pero dos registros no permiten atribuir toda la diferencia exclusivamente a la dirección del flujo ni establecer una regla general.

**Problemas observados:** O₂ aparece como `21.5 - 21.7` y `~ 21.5`. Las dimensiones visibles figuran como longitud 40,6 cm y anchura 94 cm, mientras la descripción habla de aproximadamente 0,94 m de largo y 0,4 m de ancho. Es una discrepancia de orientación/rotulado que debe resolverse antes de comparar longitudes. El espesor publicado también necesita contraste documental antes de armonizarlo con SIBAL de otras campañas. Conservar el valor original; no corregir por semejanza.

## SAFFIRE-II: mayor riqueza de resultados y mayor dificultad semántica

Comparte las primeras once columnas de SAFFIRE-I, con cambios de encabezado: `Samle Thickness`, `Sample Length`, `Sample Width (cm)` y `Percent O2 (Note 1)`. Añade estas cuatro antes de las cámaras:

| Encabezado visible | Valores observados | Decisión |
|---|---|---|
| ?-g Burn Length | `~ 0`, `29 cm`, `5 cm & 0 (note 2)`, longitud dañada | Separar longitud numérica de resultado categórico, componente y definición |
| ?-g Spread Length | `2.1 mm/s`, `2.6 mm/s`, `Note 4`, `n/a` | Encabezado incompatible con unidades de velocidad: revisión requerida antes de asignar magnitud |
| 1-g Burn Length | `Complete`, `7.6 cm`, `~ 0` | Guardar longitud y extensión cualitativa en campos distintos |
| 1-g Spread Rate | `1.2 mm/s`, `0.6 mm/s`, `Acceleratory`, `n/a` | Separar tasa numérica de comportamiento de propagación |

El carácter `?` del encabezado no debe transformarse silenciosamente en una condición de gravedad confirmada. Hay que verificar el documento de origen y vincular las condiciones de los ensayos terrestres usados como comparación.

Otros puntos relevantes:

- La nota 1 declara que O₂ se deriva de producción de CO₂, referenciada al O₂ inicial comunicado por la ISS. Es una estimación derivada, no la misma medición que el O₂ calibrado de BASS-II.
- `Burn Time` contiene `Insignificant`: no convertir en cero segundos.
- En muestras 2-6 y 2-9 el material está vacío. No rellenar automáticamente con la fila anterior.
- Espesores como `037 mm` requieren revisión; no interpretar automáticamente como 37 mm ni como 0,37 mm.
- La muestra 2-7 contiene PMMA y Nomex, con dimensiones y resultados distintos para cada componente. Una sola categoría o un promedio destruye información.
- La muestra 2-8 remite a una figura para el espesor. La geometría no queda definida por un único número en la tabla.
- Las notas distinguen consumo completo, no ignición, daño visible y una regresión lenta de una llama anclada. No todos son medidas equivalentes de propagación.
- Los identificadores de cámara muestran valores repetidos o sospechosos, como `S4C1` en ambas columnas y `S56C2`. Mantenerlos y verificarlos antes de enlazar archivos.

**Uso recomendado:** comparación descriptiva de muestras y resultados de 1g/gravedad reducida una vez aclarados encabezados y condiciones. No calcular razones de velocidades cuando alguno de los resultados sea cualitativo o no comparable.

## SAFFIRE-III: descripción de condiciones, sin resultados resumidos suficientes

Columnas: `Sample Number`, `Material`, `Sample Thickness`, `Sample Length`, `Sample Width`, `Air Flow`, `Direction`, `Camera 1`, `Camera 2`.

La tabla muestra SIBAL, dimensiones, aire a 30 cm/s y direcciones concurrente/opuesta. No incluye columnas de O₂, presión, potencia/tiempo de encendido, duración de combustión ni tasa de propagación. Esos campos deben aparecer como “no disponible en esta tabla”, sin copiar los de SAFFIRE-I.

Es útil para buscar ensayos por material, geometría y dirección; por sí sola no sostiene una gráfica de duración o velocidad de propagación. Las unidades están dentro de las celdas, por ejemplo `.33 cm` y `30 cm/s`.

## BASS: índice de ensayos y muestras

| Columna | Evaluación y uso |
|---|---|
| Date | Cronología; conservar texto original y fecha interpretada por separado |
| GMT | Los valores visibles como 90 y 96 parecen día del año, no hora UTC. Confirmar definición antes de mapear a una hora |
| As Run Test # | Orden operativo; tiene repeticiones, por lo que no es clave única |
| Test # | Identificador textual: incluye `12-R`, `12-R2`, `82a`, etc. |
| Sample # | Relaciona varios registros con una misma muestra; no identifica un ensayo único |
| Fuel Sample Material | Mezcla material, geometría, tamaño, orientación y notas; separar solo lo explícito |

Ejemplos de calidad: fecha `5/15/2103`; fecha `6/29/`12`; diferencias de día del año frente a fecha; una fila `SOOT Cleaning`; nombres `PMMA`, `pmma`, `paraffin` y `parrafin`. Existen descripciones como `2 cm sphere` sin material explícito: no completar PMMA sin otra evidencia.

**Uso recomendado:** catálogo navegable y relación ensayo–muestra–documentación. Esta tabla no incluye O₂, velocidad del aire numérica, duración, presión o resultados de extinción. No permite calcular por sí sola fronteras de inflamabilidad.

## BASS-II: condiciones, lecturas de gases y protocolo variable

| Columnas originales | Uso recomendado | Precaución |
|---|---|---|
| PI | Agrupación por investigador | No es una variable física ni una clase de riesgo |
| Test #, Sample # | Identidad y relación entre muestras y ensayos | Mantener sufijos `a/b`, `m/M` y origen |
| Date, GMT | Cronología | Fechas sospechosas; GMT no debe asumirse hora |
| Fuel Sample Material | Material y geometría | Mezcla pulgadas, mm, micras, anchura, caras y notas |
| Flow restrictor | Configuración del montaje | Categoría/código pendiente de diccionario, no caudal |
| Fan display | Registro operativo del ventilador | Incluye potenciómetro, lectura, secuencias y texto; no una velocidad escalar |
| Air display | Lecturas/secuencia del aire | No tiene unidad explícita en el encabezado; interpretar con documentación y calibración |
| Radiometer gain (1000 250 50 10) | Metadato instrumental | Ganancia no equivale a radiación medida; puede cambiar durante el ensayo |
| Total Frames Shot | Disponibilidad de adquisición | Valores como `none`, `video`, `300+ +102`; no tiempo de combustión |
| Calibrated initial O2 % by vol, Calibrated final O2 % by vol | Lecturas inicial/final de oxígeno | Validar anomalías; dos puntos no son una serie temporal |
| Initial CO2 % by vol, Final CO2 % by vol | Cambio de fracción volumétrica | Diferencia en puntos porcentuales; no producción total de masa |
| Initial CO (ppm), Final CO (ppm) | Cambio de concentración | Negativos, ausencia y sobreescala requieren estados propios |

Ejemplos: O₂ final de B2 = 1,6 %, P22b = 39,1 % y T28b = 40,4 %; CO negativo; valores `OR`, `over`, `>500`; fechas de T9/T18 en 2018 dentro de registros mayoritariamente de 2014. Requieren revisión, no sustitución automática. La tabla también contiene ensayos O20–O22 fechados en 2016: no asumir que toda la tabla pertenece a un único año.

El flujo puede cambiar varias veces dentro de un ensayo. Una secuencia como `10 5 3 0` no proporciona por sí sola los instantes de cambio ni su correspondencia con la extinción. Se necesita una relación de etapas con orden, valores y, cuando exista, tiempo. No inventar alineaciones entre listas de longitudes diferentes.

**Visualizaciones posibles:** lecturas de O₂ inicial/final por ensayo y diferencias de CO/CO₂, con indicadores de calidad. Las gráficas de frontera de extinción, calor liberado o tasa de propagación necesitan información adicional de publicaciones o archivos tabulares. La tabla no contiene un resultado de extinción estructurado.

## Modelo recomendado para el aplicativo

Separar investigación, muestra/componente, ensayo, etapa de condiciones, observación, recurso y nota. Una clave interna debe incluir la investigación y preservar los identificadores publicados: `S1` se repite entre campañas y `As Run Test #` no siempre es único.

Para cada valor conservar `texto_original`, magnitud, unidad original, valor normalizado, calificador y estado de revisión. Los estados deben distinguir numérico, aproximado, intervalo, límite, cualitativo, ausente, no aplicable, sobreescala y sospechoso. Una observación también necesita método y condición de gravedad.

Conservar origen de cada dato: PSI, versión, tabla, identificador de fila y nota vinculada. Las interpretaciones de IA deben aparecer como interpretaciones y remitir a esos registros; los campos inciertos no deben completarse con una respuesta plausible.

### Funciones que estas tablas permiten priorizar

1. Buscador por investigación y material, mostrando cobertura real de campos.
2. Ficha del ensayo con condiciones, resultados disponibles, notas y fuente.
3. Comparador que indique coincidencias, diferencias y campos ausentes.
4. Gráficas habilitadas solo para magnitudes numéricas compatibles y datos revisados.
5. Vista de calidad con valores sospechosos y decisiones de normalización.

Filtros de geometría, flujo y oxígeno deben mostrar “sin dato” y advertir que dependen de la cobertura de cada tabla. No excluir silenciosamente BASS o SAFFIRE-III como si fueran resultados negativos al aplicar un filtro de O₂.

**Orden sugerido:** usar SAFFIRE-I para demostrar fichas simples; BASS-II para explorar condiciones y gases; SAFFIRE-II para comparaciones científicas con notas y revisión; BASS y SAFFIRE-III como catálogo hasta enriquecerlos. El tamaño total de un repositorio no determina la riqueza de su tabla de resumen.

Estas tablas permiten un MVP de exploración y comparación de evidencia. Por su tamaño efectivo, resultados heterogéneos, dependencia entre muestras reutilizadas y campos ausentes, no bastan para entrenar y validar un predictor general de riesgo de incendio. Tampoco las variaciones de gases permiten por sí solas calcular toxicidad, producción total o liberación de calor sin volumen, presión, temperatura, duración y un método aplicable.
