
# Decisiones de diseño

## Lambda y no Kappa

Kappa solo utiliza procesamiento en tiempo real (streaming), con un único camino para todos los datos. En este proyecto la mayoría de las fuentes son archivos CSV que llegan periódicamente (billing, tickets, usuarios, etc.), no en tiempo real. Usar Kappa obligaría a procesar esos datos como si fueran un stream cuando no lo son. Lambda permite tener un camino batch para los CSV y un camino streaming solo para usage_events_stream, que es la única fuente que llega en tiempo real.

## Los costos negativos de billing_monthly no van a Quarantine

En billing_monthly encontramos 13 facturas con subtotal negativo dinde la más baja es de -1671.83. Decidimos mantenerlas en el pipeline marcadas como créditos y no enviarlas a Quarantine por que probablemente son créditos del proveedor de nube, como devoluciones o ajustes por compromisos de uso, y el impuesto no la confirma: en los 13 registros negativos, el tax siempre es el 21% del valor absoluto del subtotal, esto es un patrón compatible tanto con créditos como con un cambio de signo. Si las enviáramos a Quarantine, el gasto neto mensual quedaría inflado y FinOps estaría tomando decisiones sobre números incorrectos; además, el diseño no corrige los datos en cuarentena, así que quedarían afuera de los totales.
## Los costos negativos de usage_events_stream sí van a Quarantine

En usage_events_stream encontramos cost_usd_increment con valores hasta -154.46. A diferencia de billing, acá no tiene sentido de negocio: un recurso de nube no puede generar un consumo físico negativo, por eso la tratamos  como anomalías yla enviamos  a Quarantine.Concretamente, solo van a Quarantine los eventos con cost_usd_increment menor a -0,01 que son en total 211 eventos; los 5 eventos con costo entre -0,01 y 0 pasan a Silver.
## Se particiona por year/month

Particionamos los eventos solo por year/month, lo cual nos deja 2 carpetas de 20.880 y 22.320 eventos, y los 3 maestros que pasamos a Bronze  que son :clientes, usuarios y billing, también lo guardamos particionados, porque sirve para procesar y reprocesar los datos por período,  donde las consultas por organización las hacen FinOps, Soporte y Producto sobre Cassandra/AstraDB, no sobre los archivos del data lake.

Para los maestros elegimos columnas de baja cardinalidad, para que la partición sirva para filtrar sin generar muchas carpetas: customers_orgs por plan_tier  donde queda en 4 carpetas, users por role en 6 carpetas y billing_monthly por month en 3 carpetas de 80 filas, una por  cada mes facturado. Como las tablas son chicas, usamos coalesce(1) para escribir un solo archivo por carpeta; los tamaños los ponemos como evidencia en la salida del notebook 02.

## Los nulos de carbon_kg no van a Quarantine

En la exploración se verificamos que los 10.800 registros con carbon_kg nulo coinciden exactamente con los registros de schema_version = 1. Eso indica que es una evolución del esquema y no un error aleatorio, donde la versión 1 simplemente no incluía ese campo. Por lo que mandarlos a Quarantine eliminaría una cuarta parte del historial de eventos sin razón válida.

## Se usa Parquet y no CSV en Bronze, Silver y Gold

Por que parquet guarda los datos por columnas y comprimidos.Si PySpark necesita solo algunos campos, lee solo esas columnas sin abrir el archivo completo. Con 43.200 eventos y múltiples tablas, esto hace el procesamiento más rápido y ocupa menos espacio que CSV.

## El watermark es de 10 minutos

Decidimos usar un watermark de 10 minutos sobre el campo timestamp de usage_events_stream, y ordenar los eventos por timestamp antes de enviarlos al stream. El watermark le dice a Spark hasta cuándo esperar eventos que llegan tarde. Elegimos 10 minutos porque es un valor intermedio para que el sistema funcione de forma continua, ya que los eventos llegarían casi en orden: con 1 hora Spark guardaría en memoria eventos de la última hora sin necesidad, y con 1 minuto correríamos el riesgo de descartar eventos válidos que llegaron un poco tarde. El orden previo es necesario porque los 120 archivos no están ordenados cronológicamente: cada uno abarca casi todo el rango, y si los procesáramos tal como están, cerca del 98,3 % de los eventos se marcaría como tardío.
Ademas para el manejo de late data hicimos una prueba controlada enviando un evento con un timestamp anterior al watermark, y verificamos que Spark lo descarta y lo registra en la métrica .La evidencia se ecunetra en en evidence/04_pipeline_spark.

## La tabla de Cassandra guarda juntas las filas de cada organización

Se tomo la decison de que la tabla org_daily_usage_by_service en Cassandra tenga como clave primaria ((org_id), usage_date, service). Esto hace que Cassandra guarde juntas todas las filas de una organización, ordenadas por fecha y después por servicio. Lo elegimos porque FinOps, Soporte y Producto siempre consultan una organización en un período, y con esta clave la consulta lee solo los datos de esa organización y filtra el rango de fechas. Además, el servicio forma parte de la clave para que dos servicios de la misma organización en el mismo día no se pisen entre sí.Con esta clave, Cassandra no deja agrupar solo por servicio  ya que CQL exige agrupar siguiendo el orden de la clave, por eso la suma de costos por servicio de la consulta 2 se hace en Python.

## Los eventos sin unit no van a Quarantine

Completamos el campo unit en los eventos que lo traen vacío y no lo enviamos a Quarantine. En los datos pudimos ver que cada métrica siempre usa la misma unidad: donde requests es count, cpu_hours es hours y storage_gb_hours es gb_hours. Por lo que con esa base asumimos que los eventos sin unidad usan la misma que el resto de su métrica y dejamos la marca unit_imputed para saber cuáles se completaron. Esto es una suposición que sale de los datos, no de una especificación del proveedor.Ademas si los enviáramos a Quarantine junto con los costos negativos quedaría afuera el 5,28 % de los eventos y no cumpliríamos el objetivo que habíamos definido de menos del 5 %.

## Los duplicados se sacan en Bronze y no en Silver

Decidimos sacar los duplicados en Bronze en los maestros por su clave y en los eventos por event_id. En el diseño original estos  se encontraban en Silver, pero al implementarlo lo ubicamos en Bronze, así Silver recibe los datos sin repetidos. Luego lo probamos re-ejecutando el proceso y enviando un archivo repetido y en los dos casos Bronze siguió con 43.200 eventos.

## Gold se calcula en batch

Se calcula Gold en batch y no en streaming.Esto figuraba como streaming en el documento original, pero Gold lee todo lo que está guardado en Silver y suma por organización, día y servicio. El total de un día se calcula juntando todos los eventos de ese día, por eso lo hacemos sobre los datos ya guardados.

## El esquema v1/v2 se unifica en Bronze

Unificamos el esquema v1/v2 al leer los eventos en Bronze. En el diseño original estaba en Silver, pero el stream necesita que le definamos el esquema antes de leer, y ahí incluimos carbon_kg y genai_tokens. Por lo cual los eventos v1 no traen esos campos y quedan en nulo.
