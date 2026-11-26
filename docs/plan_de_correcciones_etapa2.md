# Plan de correcciones de la segunda entrega
La segunda entrega se realizo el 18/11/2026 y cada corrección sale de la devolución de ese día. 

### Ingesta desde los archivos originales
- LO Marcamos como prioridad 1
- Responsable: Mariana Wagner
- Fecha de cierre: 23/11
-En la devolucion se marco que Bronze no leía los 120 archivos originales, sino un replay ordenado por timestamp. Eso evitaba el problema de los datos tardíos en vez de resolverlo.
- lo que decidmos hacer es : sacar el replay y Bronze lee directo los 120 archivos originales. Asi el watermark pasó a la hora de llegada en ingest_ts, y no se descarta ningún evento por su fecha, y Silver y Gold siguen calculando por la fecha del evento. Ademas dejamos en el notebook la prueba que lee los archivos originales con el watermark por fecha del evento, para mostrar por qué no lo usamos: con ese watermark se pierde alrededor del 98,3 % de los eventos.
- Evidencia:  se encuentra en la celdas 10, 11, 12 y 23 del notebook 02, donde se ve que Bronze tiene 43.200 eventos leídos en 12 micro-lotes desde los archivos originales. Tambien en las capturas 02_archivos_originales.png, 03_bronze_eventos.png y 08_datos_tardios.png de evidence/04_pipeline_spark/, y en decisiones.md, el documento de diseño, el gobierno y pruebas_y_reproducibilidad.md.


### Gobierno: consecuencias del cambio en la ingesta
- Lo marcamos como prioridad 2
- Responsable: Mariana Wagner
- En la devolución se marcó que el replay tenía que aparecer en el gobierno como una transformación intermedia, con sus consecuencias explicadas.
- Fecha de cierre: el 23/11 se corigio el linaje, donde sacamos el replay y Bronze ahora lee directo desde Landing, y la regla de duplicados, donde explicamos que con el watermark sobre ingest_ts Bronze solo saca los repetidos que llegan con menos de 10 minutos de diferencia y los que llegan más tarde se sacan en Gold, que se vuelve a calcular en batch con todo Silver.
- Evidencia: Se encuentra en docs/gobierno_preliminar.md, en la regla de duplicados de Controles iniciales y en el linaje de usage_events_stream.

  
### coalesce(1) en Gold
- Lo marcamos como prioridad 3
- Responsable: Mariana Wagner
- En la devolución se marcó que usar coalesce(1) para Gold no sería adecuado al escalar.
- Fecha de cierre: el 23/11 se saco el coalesce(1) de org_daily_usage_by_service y de cost_anomaly_mart, y ahora se escriben particionados por year y month como Bronze y Silver.
- Evidencia: Se encuentra en las celdas 16 y 17 del notebook 02, y en la sección 10 del documento de diseño.

  
### Pruebas automáticas y configuración
- Lo marcamos como prioridad 1
- Responsable: Mariana Wagner
- En la devolución se marcó que las pruebas eran manuales dentro del notebook, que no había pruebas automáticas y que la configuración estaba en las celdas.
- Fecha de cierre: el 23/11 se pasaron las rutas y los parámetros a config/pipeline.yml, que lee el notebook, se llevó el cálculo de Gold a src/gold.py y se armó tests/test_pipeline.py, que hace 21 verificaciones con un solo comando: conteos de cada capa, reglas de calidad, Gold, repetidos, watermark sobre ingest_ts e idempotencia.
- Evidencia: Se encuentra en config/pipeline.yml, src/gold.py, tests/test_pipeline.py, la última celda del notebook 02 y la captura 13_pruebas_automaticas.png de evidence/04_pipeline_spark/.


### Consulta 2 de Cassandra
- Lo marcamos como prioridad 2
- Responsable: Mariana Wagner
- Fecha de cierre: el 23/11 la consulta 2 dejó de sumar y ordenar en Python. Armamos en Gold el costo de cada servicio en los últimos 14 días y en Cassandra la tabla org_top_services_14d, ordenada por costo de mayor a menor, así la consulta trae el resultado listo.
- Evidencia: Se encuentra en src/serving_cassandra.cql, en el notebook 02 y en las capturas 03a a 03d de evidence/03_serving_cassandra/.
