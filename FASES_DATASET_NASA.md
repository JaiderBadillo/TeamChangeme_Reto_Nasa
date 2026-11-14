# Fases de trabajo del dataset NASA

## 1. Seleccionar fuentes y definir la unidad de registro

Completada. La tabla temporal toma una fila por instante de adquisición publicado para cada ensayo calibrado de SAFFIRE. Las condiciones de BASS y BASS-II se entregan como observaciones de ensayo. Sus CSV de resumen proporcionaron 735 observaciones que pasan el filtro estructural anterior. Los límites e intervalos conservan sus calificadores.

## 2. Verificar el tiempo dentro de cada ensayo

Completada para los 13 ensayos calibrados. Se verificaron la unicidad y el orden creciente de los tiempos y su concordancia con el epoch publicado. La tolerancia elegida para esta comprobación fue 0,5 ms. El máximo observado fue 0,00000031 ms, residual de la representación numérica. Esta concordancia comprueba el eje común dentro de cada ensayo. La exactitud absoluta del reloj y el retardo de respuesta de cada sensor requieren otras evidencias.

`time_s` se calcula desde el primer registro del ensayo mediante diferencias de epoch enteras en milisegundos. El instante cero es el inicio del registro. Las señales se conservan en sus instantes nativos.

## 3. Aplicar controles de calidad por canal

Completada para las reglas declaradas de los 29 canales exportados. Se verificó la unidad publicada por cada archivo y se normalizó su escritura. Se enmascararon los valores no finitos y los que incumplían los límites de plausibilidad definidos en el script. Los valores afectados se exportan como nulos y la tabla de calidad registra los recuentos por ensayo y canal.

La regla de velocidad del ventilador enmascara valores negativos porque el campo declara rapidez en rpm. Los negativos en radiometría, anemometría y corriente se conservan, ya que requieren revisar el cero instrumental y la convención de signo. El canal de voltaje del encendedor queda pendiente de comprobar la escala. La revisión de saturación, calibración independiente y retardos instrumentales sigue abierta.

## 4. Alinear telemetría y admitir registros nuevos

Se auditaron las cuatro hojas RawData con pares Cygnus–SAFFIRE. Los desfases varían por archivo y hay marcas de reloj incompatibles entre representaciones. El trabajo pendiente es resolver segmentos y reinicios con referencias independientes, validar el error en pares reservados y verificar la identidad y las unidades de los canales. Cada lectura añadida necesita origen, reloj verificable, unidad confirmada y una clave que evite contarla dos veces. Se admitieron cero filas de esta telemetría en esta versión.

La búsqueda adicional en archivos comprimidos queda sujeta a identificar tablas numéricas y sus metadatos de adquisición. El número de filas final depende de cuántas superen estos controles.

## 5. Publicar y verificar la vista del aplicativo

Completada para el alcance calibrado. `sensores_sincronizados.parquet` contiene 225.300 filas. La clave temporal es `(experiment_id, time_s)`. `calidad_canales.csv` documenta unidades y recuentos. `verificacion_relojes.csv` contiene controles por ensayo y `auditoria_telemetria.csv` registra la evaluación de los relojes cruzados.

Para regenerar desde la raíz con el entorno del proyecto, ejecutar `python -m src.clean_synchronized`.

## Seguimiento de sincronización cruzada

La versión v0.5 incorporó 846 filas Cygnus de SAFFIRE-III. El maestro histórico conserva 420.421 filas, de las cuales 419.558 son eventos temporales. La vista histórica de 330.479 filas aplicaba un filtro de presencia de reloj.

`python -m src.audit_clock_segments` concilia el maestro con la entrega sincronizada y evalúa deriva lineal e interpolación local en cuatro tramos por fuente ordenados por tiempo. Los modelos se estiman con pares alternos y se comprueban con los pares reservados. El límite de 3 ms se aplica al máximo residual de cada tramo. La aceptación de un tramo tampoco basta para admitir datos. Se exige cobertura de las ventanas calibradas, respaldo cercano e identidad del canal.

SAFFIRE-I y la segunda fuente de SAFFIRE-III excedieron el límite en todos sus tramos. SAFFIRE-II presentó tres tramos con residual dentro del límite. La telemetría Cygnus utilizable en esa fuente termina antes de las ventanas calibradas una vez aplicada la relación observada entre los relojes. Esta auditoría no incorpora filas nuevas. Los modelos y residuos quedan en `data/synchronized/auditoria_desfases_por_tramo.csv`.
