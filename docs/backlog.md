# Backlog final

En este backlog dejamos lo que nos falta para la entrega final del 09/12 donde lo separamos por  obligatorio,  deseable y lo que queda fuera de alcance para que sea mas entendible:

## Obligatorio

- Cargar cost_anomaly_mart en Cassandra para poder consultarlo.
- Completar el documento de gobierno con seguridad y monitoreo.
- Armar el diccionario de datos, la presentación y el video.
- Probar el README desde cero con otra cuenta, para ver que cualquiera lo pueda ejecutar.

## Hecho

- Armamos los marts de Gold que faltaban: revenue_by_org_month, tickets_by_org_date y genai_tokens_by_org_date.
- Pasamos support_tickets a Bronze y a Silver, con su regla de Quarantine y el join con customers_orgs.
- Creamos en Cassandra una tabla para cada una de las cinco consultas.
- Agregamos el manejo de errores con consulta.exception() y una celda de limpieza para reiniciar el pipeline desde cero.

## Deseable

- Tenemos que pasar a Bronze y Silver las tablas que todavía no procesamos: resources, marketing_touches y nps_surveys.
- Aplicar en Silver la regla del NPS fuera de rango (encontramos un valor de 101).
- El poder medir si cumplimos los objetivos del documento de diseño: 60 segundos en streaming y menos de 30 minutos en batch.
- Evitar tener que volver a subir el archivo de Astra cada vez que Colab se reinicia.
- Borrar los registros de Quarantine después de 90 días, como dice el gobierno.
- Pasar el código de los notebooks a archivos .py en src/.

## Fuera de alcance

- Tenemos por un lado lo de leer los eventos desde Kafka, porque la fuente es una carpeta de archivos JSONL. Y por otro lado lo de usar Delta Lake.
