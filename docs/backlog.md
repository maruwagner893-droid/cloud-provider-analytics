# Backlog final

En este backlog dejamos lo que nos falta para la entrega final del 09/12 donde lo separamos por  obligatorio,  deseable y lo que queda fuera de alcance para que sea mas entendible:

## Obligatorio

- Cargar cost_anomaly_mart en Cassandra para poder consultarlo.
- Armar el diccionario de datos, la presentación y el video.
- Probar el README desde cero con otra cuenta, para ver que cualquiera lo pueda ejecutar.

## Hecho

- Armamos los marts de Gold que faltaban: revenue_by_org_month, tickets_by_org_date y genai_tokens_by_org_date.
- Pasamos support_tickets a Bronze y a Silver, con su regla de Quarantine y el join con customers_orgs.
- Creamos en Cassandra una tabla para cada una de las cinco consultas.
- Agregamos el manejo de errores con consulta.exception() y una celda de limpieza para reiniciar el pipeline desde cero.
- Completamos el gobierno con observabilidad y medimos los objetivos de 60 segundos y 30 minutos con dos pruebas.

## Deseable

- Tenemos que pasar a Bronze y Silver las tablas que todavía no procesamos: resources, marketing_touches y nps_surveys.
- Aplicar en Silver la regla del NPS fuera de rango (encontramos un valor de 101).
- Evitar tener que volver a subir el archivo de Astra cada vez que Colab se reinicia.
- Borrar los registros de Quarantine después de 90 días, como dice el gobierno.
- Pasar el código de los notebooks a archivos .py en src/.

## Fuera de alcance

- Tenemos por un lado lo de leer los eventos desde Kafka, porque la fuente es una carpeta de archivos JSONL. Y por otro lado lo de usar Delta Lake.

  ## Lo que hicimos para la entrega final

Para la entrega final pasamos support_tickets a Bronze y a Silver, donde los tickets sin ticket_id o sin created_at van a Quarantine y se unen con customers_orgs. En Gold armamos tres marts nuevos: revenue_by_org_month, con el subtotal, los créditos y los impuestos de cada organización por mes en USD; genai_tokens_by_org_date, con los tokens y el costo de GenAI por organización y día; y tickets_by_org_date, con la cantidad de tickets, los que incumplieron el SLA, los abiertos y el CSAT promedio por organización, fecha y severidad. En Cassandra/AstraDB creamos una tabla para cada una de las cinco consultas que pide la consigna, y las cinco devuelven resultados. El mart de anomalías queda en Gold, porque ninguna de las cinco consultas lo usa.

Ademas agregamos una celda de limpieza para reiniciar el pipeline desde cero, consulta.exception() para ver si el streaming terminó con error, y dos mediciones de tiempo: desde que llega un archivo hasta que sus eventos están procesados pasan menos de 60 segundos, y desde el primer evento en Bronze hasta que todo está en Cassandra pasan menos de 30 minutos. Las pruebas automáticas pasaron de 21 a 31 verificaciones.
