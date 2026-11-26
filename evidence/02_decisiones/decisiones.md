
# Decisiones de diseño

## Lambda y no Kappa

Kappa solo utiliza procesamiento en tiempo real (streaming), con un único camino para todos los datos. En este proyecto la mayoría de las fuentes son archivos CSV que llegan periódicamente (billing, tickets, usuarios, etc.), no en tiempo real. Usar Kappa obligaría a procesar esos datos como si fueran un stream cuando no lo son. Lambda permite tener un camino batch para los CSV y un camino streaming solo para usage_events_stream, que es la única fuente que llega en tiempo real.

## Los costos negativos de billing_monthly no van a Quarantine

En billing_monthly hay 13 facturas con subtotal negativo, donde la más baja es de -1671.83. Creemos que son créditos del proveedor, como devoluciones o descuentos, así que decidimos no las mandarlas a Quarantine, si no que las dejamos y marcamos con is_credit. Si las sacáramos, FinOps vería un gasto mayor al real. Igual no podemos asegurar que no sean errores, por eso quedan marcadas para poder revisarlas.

En usage_events_stream encontramos cost_usd_increment con valores hasta -154.46. A diferencia de billing, acá no tiene sentido de negocio: un recurso de nube no puede generar un consumo físico negativo, por eso la tratamos  como anomalías yla enviamos  a Quarantine.Concretamente, solo van a Quarantine los eventos con cost_usd_increment menor a -0,01 que son en total 211 eventos; los 5 eventos con costo entre -0,01 y 0 pasan a Silver.

## Se particiona por year/month

Particionamos los eventos solo por year/month, lo cual nos deja 2 carpetas de 20.880 y 22.320 eventos, y los 3 maestros que pasamos a Bronze  que son :clientes, usuarios y billing, también lo guardamos particionados, porque sirve para procesar y reprocesar los datos por período,  donde las consultas por organización las hacen FinOps, Soporte y Producto sobre Cassandra/AstraDB, no sobre los archivos del data lake.

   Para los maestros elegimos columnas de baja cardinalidad, para que la partición sirva para filtrar sin generar muchas carpetas: customers_orgs por plan_tier  donde queda en 4 carpetas, users por role en 6 carpetas, billing_monthly por month en 3 carpetas de 80 filas, una por  cada mes facturado, y support_tickets por severity en 4 carpetas. Como las tablas son chicas, usamos coalesce(1) para escribir un solo archivo por carpeta; los tamaños los ponemos como evidencia en la salida del notebook 02.

## El coalesce(1) queda solo en tablas chicas y en cada micro-lote de Silver

  En Gold sacamos el coalesce(1) porque se aplicaba a toda la tabla de una vez, y si crecen los datos una sola tarea tendría que escribir todo. En Silver y Quarantine de eventos lo dejamos porque se aplica dentro de cada micro-lote del foreachBatch, y cada micro-lote lee como máximo 10 archivos de Bronze por el maxFilesPerTrigger, asi que aunque crezcan los datos cada lote sigue siendo chico. Sin el coalesce(1) cada micro-lote podría escribir varios archivos por mes y terminar en muchos archivos chicos. Silver de tickets y los marts de Gold se escriben sin coalesce(1).
  
## Los nulos de carbon_kg no van a Quarantine

En la exploración se verificamos que los 10.800 registros con carbon_kg nulo coinciden exactamente con los registros de schema_version = 1. Eso indica que es una evolución del esquema y no un error aleatorio, donde la versión 1 simplemente no incluía ese campo. Por lo que mandarlos a Quarantine eliminaría una cuarta parte del historial de eventos sin razón válida.

## Se usa Parquet y no CSV en Bronze, Silver y Gold

Por que parquet guarda los datos por columnas y comprimidos.Si PySpark necesita solo algunos campos, lee solo esas columnas sin abrir el archivo completo. Con 43.200 eventos y múltiples tablas, esto hace el procesamiento más rápido y ocupa menos espacio que CSV.

## El watermark es de 10 minutos

Decidimos usar un watermark de 10 minutos sobre ingest_ts, que es la hora en que llega cada evento, y no sobre timestamp. Esto lo cambiamos porque cuando exploramos los datos vimos que los 120 archivos no están ordenados, cada uno tiene eventos desde el 03/07/2025 hasta el 31/08/2025. Si usamos el watermark de 10 minutos con timestamp se descarta casi el 98,3 % de los eventos. Para que no se pierda ninguno tendríamos que esperar los 60 días del dataset.
Ademas con ingest_ts entran todos los eventos a Bronze y se sacan los repetidos por event_id. El timestamp queda igual y lo usamos en Silver y Gold para calcular las métricas. Como Gold se vuelve a calcular en batch con todo lo que hay en Silver, los eventos que llegan tarde también se cuentan.
Ademas para el manejo de late data hicimos una prueba controlada con un watermark sobre timestamp, enviando un evento con fecha anterior al watermark, y verificamos que Spark lo descarta y lo registra en la métrica numRowsDroppedByWatermark. Esa prueba muestra cómo funciona el watermark por fecha del evento; en Bronze no lo usamos, por lo explicado arriba. La evidencia se ecunetra en en evidence/04_pipeline_spark.
## La tabla de Cassandra guarda juntas las filas de cada organización

Se tomo la decison de que la tabla org_daily_usage_by_service en Cassandra tenga como clave primaria ((org_id), usage_date, service). Esto hace que Cassandra guarde juntas todas las filas de una organización, ordenadas por fecha y después por servicio. Lo elegimos porque FinOps, Soporte y Producto siempre consultan una organización en un período, y con esta clave la consulta lee solo los datos de esa organización y filtra el rango de fechas. Además, el servicio forma parte de la clave para que dos servicios de la misma organización en el mismo día no se pisen entre sí. Con esta clave Cassandra no deja agrupar solo por servicio, ya que CQL exige seguir el orden de la clave. Por eso para la consulta 2 armamos una segunda tabla, org_top_services_14d, siguiendo la regla de una tabla por consulta. Su clave es: ((org_id, window_end), cost_usd_14d, service), ordenada por costo de mayor a menor: la partición es la organización y el último día de la ventana de 14 días, y adentro los servicios quedan ordenados por costo. El costo de cada servicio en los 14 días lo calcula Spark en Gold, así Cassandra devuelve el resultado listo, sin sumar ni ordenar en Python. Como el costo es parte de la clave, si se recalcula la misma ventana con datos distintos el INSERT no pisa la fila anterior sino que agrega otra, por lo que en ese caso habría que borrar antes esa partición.

## Los eventos sin unit no van a Quarantine

Completamos el campo unit en los eventos que lo traen vacío y no lo enviamos a Quarantine. En los datos pudimos ver que cada métrica siempre usa la misma unidad: donde requests es count, cpu_hours es hours y storage_gb_hours es gb_hours. Por lo que con esa base asumimos que los eventos sin unidad usan la misma que el resto de su métrica y dejamos la marca unit_imputed para saber cuáles se completaron. Esto es una suposición que sale de los datos, no de una especificación del proveedor.Ademas si los enviáramos a Quarantine junto con los costos negativos quedaría afuera el 5,28 % de los eventos y no cumpliríamos el objetivo que habíamos definido de menos del 5 %.

## Los duplicados se sacan en Bronze y no en Silver

Decidimos sacar los duplicados en Bronze en los maestros por su clave y en los eventos por event_id. En el diseño original estos  se encontraban en Silver, pero al implementarlo lo ubicamos en Bronze, así Silver recibe los datos sin repetidos. Luego lo probamos re-ejecutando el proceso y enviando un archivo repetido y en los dos casos Bronze siguió con 43.200 eventos.

## Gold se calcula en batch

Se calcula Gold en batch y no en streaming.Esto figuraba como streaming en el documento original, pero Gold lee todo lo que está guardado en Silver y suma por organización, día y servicio. El total de un día se calcula juntando todos los eventos de ese día, por eso lo hacemos sobre los datos ya guardados.

## El esquema v1/v2 se unifica en Bronze

Unificamos el esquema v1/v2 al leer los eventos en Bronze. En el diseño original estaba en Silver, pero el stream necesita que le definamos el esquema antes de leer, y ahí incluimos carbon_kg y genai_tokens. Por lo cual los eventos v1 no traen esos campos y quedan en nulo.

## Las anomalías de costo se detectan con un método por percentiles (IQR)

Para el componente analítico decidimos por el mart cost_anomaly_mart, con grano org_id, usage_date y service, a partir de la columna daily_cost_usd del mart org_daily_usage_by_service. Por ello usamos un método por percentiles que es el rango intercuartílico (IQR),  para cada organización y servicio.Lo elegimos frente al z-score porque es el método que usamos en Minería de Datos I para detectar valores atípicos, con el límite superior q3 + 1,5 × iqr. Además, cuando hay un pico muy grande el promedio sube y algunos picos más chicos dejan de verse, y con los cuartiles eso no pasa.
Ademas solo marcamos los días por encima del límite superior, porque buscamos los picos de costo que menciona la consigna. Los días por debajo del límite inferior son costos cercanos a cero,  por lo cual no representan un riesgo para FinOps. Con este criterio se marcan 196 de los 11.050 días que es el 1,77 %. Cada combinación de organización y servicio tiene entre 24 y 60 días de datos, por lo que los percentiles se calculan sobre suficientes valores.

Como limitaciones, el cálculo usa todo el período, incluidos los días posteriores al día evaluado, por lo que sirve para el análisis histórico y no como alerta en tiempo real. Además, el dataset no tiene anomalías marcadas de antemano, así que no podemos medir cuántas acierta: lo que reportamos es la cantidad de días marcados y su costo comparado con el límite de su organización y servicio.
