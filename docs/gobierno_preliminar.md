
# Gobierno preliminar

## Controles iniciales
Los controles los aplicamos en cada capa del pipeline, pero no todos funcionan de la misma forma. Los registros que no cumplen una regla de rechazo van a Quarantine junto con el motivo, en la columna quarantine_reason. Los datos que llegan incompletos se completan y les dejamos una marca para saber cuáles fueron imputados. Ademas loos eventos duplicados y los que llegan tarde se eliminan.

Las reglas que aplicamos son las siguentes:
- Event_id no nulo: si un evento no tiene event_id va a Quarantine con el motivo event_id_nulo. En los datos no encontramos ninguno.
- Costo: los eventos con cost_usd_increment menor a -0,01 van a Quarantine con el motivo cost_usd_increment_menor_a_-0.01. Son 211 eventos, es decir el 0,49 %, quedando asi en Silver quedan 42.989.
- Unit: cuando  falta, decidimos completarlos según la métrica y lo marcamos con unit_imputed.Fueron 2.069 y en Silver no queda ninguna vacía.
- Duplicados: los sacamos en Bronze por event_id con un watermark de 10 minutos sobre ingest_ts, y quedan 43.200 eventos. Como el watermark va sobre la hora de llegada, Bronze solo encuentra los repetidos que llegan con menos de 10 minutos de diferencia; los que lleguen más tarde se sacan en Gold, que se vuelve a calcular en batch con todo Silver y vuelve a sacar los repetidos por event_id.
- Billing: los credits nulos los tomamos como 0 y los marcamos con credits_imputed, las facturas con subtotal negativo las marcamos con is_credit  y las que tengan tasa de cambio nula o menor o igual a 0 van a Quarantine con el motivo exchange_rate_nula_o_no_positiva. No hubo ninguna, por lo cual las 240 facturas pasan a Silver.
- Tickets: los tickets sin ticket_id o sin created_at van a Quarantine con el motivo ticket_id_nulo o created_at_nulo. No hubo ninguno, por lo cual los 1000 tickets pasan a Silver. Los nulos de resolved_at y csat se mantienen como nulos.

Además hicimos las siguentes pruebas:
- Idempotencia: volvimos a ejecutar el proceso sin archivos nuevos y con un archivo repetido, donde bronze se mantuvo en 43.200 en los dos casos y silver en 42.989.
- Archivos desordenados: con el watermark sobre timestamp y los archivos como vienen en el dataset pasaron alrededor de 733 de 43.200 eventos, es decir que se descartó el 98,3 % por tardíos. Por eso el watermark de Bronze va sobre ingest_ts, la hora de llegada, y así entran los 43.200.
- Datos tardíos: en una prueba aparte, con un watermark sobre timestamp, enviamos un evento con fecha anterior al watermark y Spark lo descartó, lo que se ve en la métrica numRowsDroppedByWatermark = 1. En Bronze el watermark va sobre ingest_ts, así que ahí no se descartan eventos por su fecha.

## Metadatos
A cada registro le agregamos columnas que indican de dónde viene y cuándo se procesó, para poder rastrearlo y controlarlo.

Metadatos de ingesta, que se agregan en Bronze a las cinco fuentes que procesamos: los maestros customers_orgs , users , billing_monthly y support_tickets, y los eventos de usage_events_stream:
- ingest_ts: fecha y hora en que el registro se cargó en Bronze.
- source_file: Es el nombre del archivo del que se leyó el registro. En los maestros es el CSV de Landing y en los eventos es el archivo JSONL original de Landing (events_part_XXXX.jsonl).
Metadatos del esquema:
- schema_version: viene en cada evento e indica la versión del esquema. Los eventos de la versión 1 no traen carbon_kg, por lo cual queda nula en ellos. Ademas genai_tokens solo viene en los eventos de la versión 2 del servicio genai, por eso en el resto queda nula.

Marcas de calidad, que se agregan en Silver:
- unit_imputed: Aca la unidad del evento se completó a partir de la métrica.
- value_missing: el evento no trae value.
- credits_imputed: en billing, teniamo que credits venía nulo y se tomó como 0.
- is_credit: en billing, la factura tiene subtotal negativo.
- is_open: en tickets, el ticket no tiene resolved_at, es decir que sigue abierto.

Metadatos de Quarantine:
- quarantine_reason: Es el  motivo por el que se rechazó el registro.
- quarantine_ts: fecha y hora en que el registro se envió a Quarantine.
- 
## Linaje
El linaje muestra de dónde sale cada dato y por qué capas pasa. Todas las rutas son carpetas dentro de data/, que el notebook crea al ejecutarse a partir del zip del dataset.

usage_events_stream:

- Landing: los 120 archivos JSONL originales, en data/extracted/datalake/landing/usage_events_stream.
- Bronze: data/bronze/usage_events_stream, leído con Structured Streaming directo desde los archivos de Landing, con watermark sobre ingest_ts.
- Silver: data/silver/usage_events, unido con customers_orgs de Bronze. Los rechazados van a data/quarantine/usage_events.
- Gold: data/gold/org_daily_usage_by_service, que se vuelve a calcular en batch con todo Silver: saca los eventos repetidos por event_id y los suma por organización, día y servicio, usando la fecha del evento. Así los eventos que llegan tarde también quedan en el día que corresponde.
- Gold: data/gold/cost_anomaly_mart, que se calcula a partir de org_daily_usage_by_service.
- Gold: data/gold/org_service_cost_14d, que suma el costo de cada servicio por organización en los últimos 14 días, a partir de org_daily_usage_by_service.
- Gold: data/gold/genai_tokens_by_org_date, que toma de org_daily_usage_by_service el servicio genai en los días con tokens.
- Serving: las tablas cloud_provider.org_daily_usage_by_service, cloud_provider.org_top_services_14d y cloud_provider.genai_tokens_by_org_date en Cassandra/AstraDB, cargadas desde Gold.

billing_monthly:

- Landing: billing_monthly.csv.
- Bronze: data/bronze/billing_monthly.
- Silver: data/silver/billing_monthly. Los rechazados van a data/quarantine/billing_monthly.
 - Gold: data/gold/revenue_by_org_month, que suma por organización y mes el subtotal, los créditos y los impuestos pasados a USD.
- Serving: la tabla cloud_provider.revenue_by_org_month en Cassandra/AstraDB.

support_tickets:

- Landing: support_tickets.csv.
- Bronze: data/bronze/support_tickets.
- Silver: data/silver/support_tickets, unido con customers_orgs de Bronze. Los rechazados van a data/quarantine/support_tickets.
- Gold: data/gold/tickets_by_org_date, que cuenta los tickets, los que incumplieron el SLA y los abiertos, y calcula el CSAT promedio por organización, fecha y severidad.
- Serving: la tabla cloud_provider.tickets_by_org_date en Cassandra/AstraDB.
  
customers_orgs y users:

- Landing: customers_orgs.csv y users.csv.
- Bronze: data/bronze/customers_orgs y data/bronze/users. customers_orgs se usa en Silver para enriquecer los eventos  y los tickets.
  
Para saber de dónde viene un registro usamos source_file, que indica el archivo del que se leyó, y la clave de cada tabla:como  event_id en los eventos,invoice_id en billing, ticket_id en tickets, org_id en clientes y user_id en usuarios.Ademas en Gold y en Cassandra los datos ya están agregados, por lo cual se siguen por su grano: org_id, usage_date y service.

## Responsabilidades
Las responsabilidades decidimos  dividirlos en dos: En primer lugar tenemos las áreas de negocio, que son dueñas de los datos que usan, y  en segundo los roles del equipo, que se encargan de construir y mantener el pipeline.

Áreas de negocio:
- FinOps: es responsable de los datos de facturación. Además tiene que confirmar el criterio de tomar credits nulo como 0, que aplicamos en Silver pero todavía está pendiente de su validación.
- Soporte: es responsable de los datos de tickets.
- Producto: es responsable de los datos de uso de los servicios  y de NPS.

Roles del equipo, según el cronograma  del documento de diseño de nuestro proyecto son los:
- Data Analyst: Que es la exploración de los datos.
- Analista de negocio y Data Engineer: El diseño de la arquitectura.
- Data Engineer: Aca tenemos el desarrollo del pipeline batch y streaming, y la carga en Cassandra.
- QA / Tester: el testing del pipeline.

Los registros que quedan en Quarantine los revisa el equipo durante los 90 días de retención, ytiene que decidir si se corrigen o se descartan definitivamente.

## Acceso
El acceso lo controlamos en dos lugares: El repositorio y Cassandra/AstraDB.

- Repositorio: tiene el dataset y el código, pero no tiene credenciales. El archivo .gitignore deja afuera el secure connect bundle (secure-connect*.zip) y el archivo .env.
- Cassandra/AstraDB: para conectarse hacen falta un token y el secure connect bundle de la base. El token se genera desde el portal de Astra con el rol Database Administrator y se guarda en los Secretos de Colab con el nombre ASTRA_TOKEN. El notebook lo lee con userdata.get, por lo cual nunca queda escrito en el código. El bundle se sube a /content/ en cada sesión de Colab.
- Si un token se filtra, se revoca desde el portal de Astra y se genera uno nuevo.

 ## Observabilidad
Para saber si el pipeline funcionó bien miramos las salidas que deja el propio notebook en cada capa:
- Streaming de Bronze: un StreamingQueryListener donde guarda por cada micro-lote el número de lote, las filas leídas y las filas por segundo de entrada y de proceso. En la última ejecución hubo 12 micro-lotes de 3.600 filas, 43.200 en total. Cuando termina la consulta, el listener muestra si hubo un error, y además se muestra consulta.exception(), que da None si terminó bien.
- Silver y Quarantine: despues de cada carga se muestran las filas que quedaron en Silver, las que fueron a Quarantine y el porcentaje de inválidos, junto con la cantidad por quarantine_reason. Hoy es 0,49 %, por debajo del 5 % que pusimos como objetivo.
- Gold y Cassandra: despues de cargar cada tabla se compara la cantidad de filas de Gold con las de Cassandra y se cuentan los errores de escritura. En las cinco tablas coinciden y hay 0 errores.
- Pruebas: la última celda corre las 30 verificaciones de tests/test_pipeline.py y dice si pasaron todas.
Para los objetivos de tiempo del documento de diseño hicimos dos mediciones. Para los 60 segundos, la prueba de latencia copia tres archivos originales mientras el stream está corriendo y mide cuánto pasa desde que llega cada archivo, con _metadata.file_modification_time, hasta que sus eventos ya están procesados, y en todos los casos tardó menos de 60 segundos; esta prueba tambien está en tests/test_pipeline.py. Para los 30 minutos, despues de la última carga en Cassandra se mide el tiempo desde que entró el primer evento a Bronze hasta ese momento, y tardó menos de 30 minutos, aun contando las celdas de prueba que están en el medio. Las capturas están en evidence/04_pipeline_spark/16_prueba_latencia.png y 17_tiempo_hasta_cassandra.png.
## Evidencias
Las evidencias de lo que se describe en este documento están en la carpeta evidence/ y en las salidas guardadas del notebook notebooks/02_pipeline_etapa2.ipynb.

- evidence/01_hallazgos_calidad/hallazgos.md:Aca se muestron lo problemas de calidad encontrados en la exploración de los datos.
- evidence/02_decisiones/decisiones.md: Son las decsiones que tomamos, como los umbrales de Quarantine, el watermark, el particionado y el método de anomalías.
- evidence/registro_calidad/registro_calidad.md: Son las reglas de calidad de cada tabla.
- evidence/04_pipeline_spark/: Aca se encuentran las capturas de la ejecución del pipeline. Muestran la ingesta en Bronze , el rango de fechas de los archivos originales, la idempotencia , Silver y Quarantine , Gold , la prueba con archivos desordenados , las rutas y tamaños de cada capa , el mart de anomalías,la prueba controlada de datos tardíos, y las pruebas del watermark sobre ingest_ts y de los repetidos en Gold.
- evidence/03_serving_cassandra/: capturas de la carga en Cassandra/AstraDB , las cinco consultas  y el keyspace en Astra.
