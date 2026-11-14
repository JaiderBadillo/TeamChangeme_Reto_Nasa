# Datos del aplicativo

La entrega v1.0 se genera con `python -m src.release_app_data`. Usa las series aprobadas en v0.5 y añade `cobertura_temporal` con los intervalos por ensayo y fuente, y `unidades_cygnus` con las unidades de los canales de telemetría. El ZIP incluye la base, el inventario de cobertura y los resultados de validación.

El archivo `nasa_app.duckdb` integra las series de la versión sincronizada v0.5 con el catálogo de ensayos. Abrir la base en modo de solo lectura desde el backend.

| Consulta | Uso |
|---|---|
| `catalogo` | Buscar por investigación, material o ensayo y comprobar qué datos tiene cada ficha |
| `serie_saffire(ensayo, desde, hasta)` | Leer canales calibrados en una ventana de tiempo |
| `serie_cygnus(ensayo, desde, hasta)` | Leer la telemetría alineada disponible para los dos ensayos de SAFFIRE-III |
| `ficha_condiciones(ensayo)` | Consultar observaciones de BASS y BASS-II con unidades, límites y procedencia |
| `unidades_saffire` y `auditoria_relojes` | Consultar unidades, controles de canales y evidencia de alineación |

```sql
SELECT experiment_id, study_name, material_original, saffire_filas, cygnus_filas
FROM catalogo WHERE saffire_filas > 0;

SELECT time_s, o2, co2 FROM serie_saffire('PSI-100:S1:r2', 0, 60);
SELECT time_s, "PCM Air Temp (degC)" FROM serie_cygnus('PSI-100:S1:r2', 0, 60);
```

El eje `time_s` parte del primer registro calibrado de cada ensayo. Superponer las series por ese eje y respetar sus frecuencias nativas. Los nulos representan ausencia de un valor utilizable y deben mostrarse como huecos. Las fichas de BASS son observaciones sin eje temporal.

El catálogo contiene 263 registros experimentales. La cobertura sincronizada incluye 225.300 filas calibradas y 846 filas Cygnus, además de 735 observaciones de condiciones. Las lecturas Cygnus conservan el intervalo entre anclas y el residual máximo observado al validar su transformación de reloj. La respuesta física del sensor puede tener retardos adicionales.

Para reconstruir este archivo desde la raíz del proyecto, ejecutar `python -m src.prepare_app_data`.
