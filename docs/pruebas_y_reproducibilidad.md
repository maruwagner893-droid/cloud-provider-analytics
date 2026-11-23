# Pruebas y reproducibilidad

## Puesta en marcha
Los pasos para poder ejecutar nuesto proyecto desde cero están en la sección cómo ejecutar del README. Al ejecutarse, el notebook notebooks/02_pipeline_etapa2.ipynb clona el repositorio, descomprime el dataset de data/ e instala PySpark y cassandra-driver de forma automática. Lo que si se debe preparar a mano es la conexión a Cassandra: crear la base en Astra DB con el keyspace cloud_provider, generar el token y descargar el secure connect bundle, y después, en Colab, guardar el token en los Secretos con el nombre ASTRA_TOKEN y subir el bundle a /content/.

Ademas la versión de PySpark que usamos es la 4.0.5, y es la única que está fijada en requirements.txt; los demás paquetes no tienen versión. En el notebook  se instala PySpark sin indicar su versión, así que en Colab se instala la última disponible.

## Configuración
La configuración está definida en las celdas del notebook y Los valores que usamos son:
- Spark: se ejecuta en modo local (local[*]) con 8 particiones de shuffle, porque el volumen de datos es chico. La zona horaria de la sesión es UTC, para que las fechas de los eventos se calculen siempre igual.
- Streaming: Bronze y Silver leen 10 archivos por micro-lote, usan el trigger availableNow, que procesa todo lo pendiente y termina, y cada consulta tiene su propio checkpoint en data/checkpoints/bronze_events y data/checkpoints/silver_events. Bronze lee directo los archivos de Landing y aplica un watermark de 10 minutos sobre ingest_ts, la hora de llegada.
- Reglas: el umbral de costo para Quarantine es -0,01 y el factor del método IQR para las anomalías es 1,5.
- Cassandra: el token se lee del secreto ASTRA_TOKEN de Colab, el bundle se busca en /content/ y la conexión usa el keyspace cloud_provider.

## Logs
Los registros de la ejecución son las salidas del notebook: print, show y explain, que quedan guardadas en el notebook, y las capturas de la carpeta evidence/.

Para el streaming, la consulta de Bronze tiene el nombre bronze_events y cada micro-lote se registra con un StreamingQueryListener, que guarda el número de micro-lote en batchId, las filas leídas en numInputRows y las filas por segundo que llegan y que se procesan en inputRowsPerSecond y en processedRowsPerSecond. Al final mostramo cuántos micro-lotes tuvieron datos y el total de filas leídas: que son  12 micro-lotes y 43.200 filas.

Los registros rechazados quedan en Quarantine con el motivo: quarantine_reason y la fecha y hora del rechazo  en quarantine_ts, lo que funciona como registro de todo lo que no pasó las reglas de calidad.

## Manejo de errores
Para los errores decidimos apoyarnos en los controles sobre los datos y sobre la re-ejecución, sin try/except en el código:
- Esquemas explícitos en todas las lecturas, para que cada columna tenga el tipo esperado.
- Reglas de calidad: los registros inválidos van a Quarantine y el proceso sigue con el resto.
- mode("overwrite") en las escrituras batch, para poder volver a ejecutar sin duplicar datos.
- Checkpoints en el streaming, para no volver a procesar archivos que ya se leyeron.
- Antes de clonar, el notebook  se tiene que verificar si el repositorio ya existe (if not os.path.exists(REPO)).

La conexión a Cassandra/AstraDB no tiene un control propio: por eso se tiene que tener encuenta que si falta el secure connect bundle o el token, la celda falla y hay que revisar el paso 5 del README.

## Pruebas
Las pruebas las hicimos a mano dentro del notebook, sin una carpeta tests/:

- Idempotencia: volvimos a ejecutar el proceso sin archivos nuevos y con un archivo repetido, y Bronze se mantuvo en 43.200 eventos. Silver también se mantuvo en 42.989.
- Archivos desordenados: con el watermark sobre timestamp y los archivos como vienen en el dataset pasaron alrededor de 733 de 43.200 eventos. Para tener encuetna el número exacto cambia levemente entre ejecuciones, porque depende del orden en que Spark lee los archivos. Con el watermark sobre ingest_ts, Bronze recibe los 43.200.
- Datos tardíos: en una prueba aparte, con un watermark sobre timestamp, un evento con fecha anterior al watermark se descarta y la métrica numRowsDroppedByWatermark marca 1. En Bronze el watermark va sobre ingest_ts, así que ahí no se descartan eventos por su fecha.
- Watermark sobre ingest_ts y repetidos tardíos: con los mismos eventos de la prueba de datos tardíos, pero con el watermark sobre ingest_ts como en Bronze, entran los 4 eventos y no se descarta ninguno. Ademas agregamos a Silver 209 eventos repetidos y Gold sigue dando 11.050 filas y 42.989 eventos, porque calcular_gold saca los repetidos por event_id.
- Conteos de cada capa: Bronze 43.200, Silver 42.989, Gold 11.050 filas y Cassandra 11.050 filas, con la misma suma de requests en Gold y en Cassandra.
- Las dos consultas CQL devuelven resultados.

Para la limpieza, el notebook solo borra lo que crean las pruebas: la carpeta de la prueba de datos tardíos y el archivo repetido de la prueba de idempotencia. No hay un procedimiento para reiniciar todo el pipeline; en Colab se logra abriendo una sesión nueva.
