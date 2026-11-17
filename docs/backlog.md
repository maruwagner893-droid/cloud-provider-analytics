# Backlog final

En este backlog dejamos lo que nos falta para la entrega final del 09/12, separado en lo obligatorio, lo deseable y lo que queda fuera de alcance.

## Obligatorio

- Armar los marts de Gold que faltan: revenue_by_org_month, tickets_by_org_date y genai_tokens_by_org_date.
- Pasar support_tickets a Bronze y a Silver, porque es la fuente del mart tickets_by_org_date.
- Crear en Cassandra una tabla para cada una de las cinco consultas obligatorias. Hoy la consulta 2 suma los costos por servicio en Python.
- Cargar el mart cost_anomaly_mart en Cassandra para poder consultarlo.
- Completar el gobierno, sumando seguridad y observabilidad.
- Sacar la configuración del notebook a un archivo aparte, agregar manejo de errores, pruebas en una carpeta tests/ y una forma de reiniciar el pipeline.
- Hacer la documentación técnica con el diccionario de datos, la presentación y el video.
- Probar el README desde cero, con otra cuenta.

## Deseable

- Pasar a Bronze y a Silver resources, marketing_touches y nps_surveys, y a Silver customers_orgs y users, incluida la regla del NPS fuera de rango.
- Medir los objetivos del documento de diseño: 60 segundos de latencia en streaming y menos de 30 minutos para el batch.
- Guardar los eventos que el watermark descarta en lugar de perderlos.
- Hacer que la escritura de Silver no duplique datos si un micro-lote se reintenta, por ejemplo con MERGE dentro de foreachBatch.
- Guardar los checkpoints en un almacenamiento que no se pierda al cerrar la sesión de Colab.
- Aplicar la retención de 90 días en Quarantine.
- Verificar los datos de Cassandra por organización, en lugar de con COUNT(*) y SUM sobre toda la tabla.
- Pasar el código de los notebooks a scripts en src/ y dejar los notebooks para la exploración y las evidencias.
- Archivar los archivos de Landing que ya se procesaron, con la opción cleanSource de Structured Streaming.
- Registrar también las métricas de cada micro-lote de Silver con StreamingQueryListener, como ya hacemos en Bronze.
## Fuera de alcance

- Leer los eventos desde Kafka, porque la consigna define como fuente una carpeta de archivos JSONL.
- Usar Delta Lake o Iceberg, porque la consigna pide Parquet.
- Usar el Real-Time Mode de Spark, porque trabajamos con los micro-lotes de Structured Streaming.
