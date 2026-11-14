# Datos de BASS y BASS-II para Flame in Freefall

El dashboard carga los archivos JSON de esta tabla. Se transcribieron las tablas indicadas del [informe NASA/TM-20210011385](https://ntrs.nasa.gov/citations/20210011385), disponible también como [PDF oficial](https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf). Las páginas indicadas son las impresas en el informe.

| Archivo | Cobertura | Localizador |
| --- | --- | --- |
| [bass_ii_pmma.json](./bass_ii_pmma.json) | Ensayos M1 a M20 completos. 43 condiciones de flujo y 39 tasas de propagación reportadas. Incluye geometría, duración de combustión y O₂ inicial/final por ensayo. | Tabla 5.1, p. 57. Montaje y método, sección 5.3. Alcance del O₂, sección 5.4 «Oxygen Concentration Analysis». |
| [bass_sibal.json](./bass_sibal.json) | 31 filas de tejido SIBAL: 4 de BASS original y 27 de BASS-II. Incluye cambios de flujo, O₂, observaciones y la nota sobre dos lecturas posiblemente inexactas. | Tabla 7.1, p. 96, sección 7.1.4. |
| [bass_pmma_appendix_d.json](./bass_pmma_appendix_d.json) | Una observación de propagación de una placa de PMMA de BASS original y cuatro quemas de la esfera de PMMA de la muestra 19. | Apéndice D.7 y figura D.6, p. 127. Tabla D.2, p. 128. |
| [bass_ii_extinction.json](./bass_ii_extinction.json) | Dos condiciones de oxígeno para la velocidad crítica de extinción a 1 atm. Conserva resultado experimental con su `±`, cálculo numérico y teoría. | Tabla 2.1, p. 28. |

## Cómo leer el JSON

- `runId` conserva el identificador de NASA cuando está publicado en el localizador. En la tabla 5.1, cada objeto en `runs` representa un ensayo y cada elemento de `conditions` un valor de flujo registrado. Se preserva el orden de la tabla.
- `oxygenInitialVolPct` y `oxygenFinalVolPct` se refieren al ensayo completo. NASA describe interpolaciones en su análisis. El JSON guarda los valores reportados al inicio y al final. Un escenario con O₂ exacto por punto requiere evidencia adicional.
- `null` indica un campo sin dato tabulado para ese registro. M6 y M12 conservan sus cuatro condiciones de flujo con tasa `null` porque el informe indica que no se siguió la propagación. Para SIBAL, la tabla 7.1 registra condiciones y observaciones. Las tasas de la figura 7.4 no se digitalizaron.
- En SIBAL, `airflowFinalCmS` se llena cuando la tabla indica un cambio. `airflowMode` distingue flujo fijo y variado. Mapea `outcome` al resultado consignado. Una fila sin observación conserva `null`. La nota sobre O₂ se aplica a GMT45-T1 y GMT45-T2.
- La tasa de propagación, el flujo crítico de extinción y la duración de combustión son magnitudes distintas. En la tabla 2.1, `experiment`, `computation` y `theory` conservan sus tipos de evidencia. En la tabla D.2, `burnDurationSec` convierte la duración publicada de horas, minutos y segundos a segundos. En la fila 21, NASA da 100 s de duración y sus horas de inicio y fin arrojan 90 s. Se conservan ambos valores y se marca la discrepancia.
- Los CSV `bass_ii_m7.csv` y `bass_sibal_concurrent.csv` conservan las extracciones iniciales para quien ya las citó.

## Fuentes y cobertura pendiente

- [BASS-II en NASA PSI](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25), DOI [10.60555/4qc4-de67](https://doi.org/10.60555/4qc4-de67). PSI lista los archivos del experimento.
- [BASS original en NASA Glenn](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/) y [presentación de resultados en NASA NTRS](https://ntrs.nasa.gov/citations/20140011099).
- Quedan por extraer matrices del apéndice A (tablas A.1 a A.6), otros resultados que NASA publica en figuras y los archivos primarios de PSI. Estas fuentes pueden describir ensayos que también aparecen en los capítulos del informe. Antes de agregarlas, vincula el número de ensayo, el número de muestra y la fecha de ejecución que dé NASA para resolver coincidencias sin duplicar ensayos.
