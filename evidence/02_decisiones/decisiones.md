
# Decisiones de diseño

## Por qué Lambda y no Kappa

Kappa solo utiliza procesamiento en tiempo real (streaming), con un único camino para todos los datos. En este proyecto la mayoría de las fuentes son archivos CSV que llegan periódicamente (billing, tickets, usuarios, etc.), no en tiempo real. Usar Kappa obligaría a procesar esos datos como si fueran un stream cuando no lo son. Lambda permite tener un camino batch para los CSV y un camino streaming solo para usage_events_stream, que es la única fuente que llega en tiempo real.

## Por qué los costos negativos de billing_monthly no van a Quarantine

En billing_monthly encontramos 13 facturas con subtotal negativo, la más baja es de -1671.83. Decidimos mantenerlas en el pipeline marcadas como créditos y no enviarlas a Quarantine. Probablemente son créditos del proveedor de nube, como devoluciones o ajustes por compromisos de uso, y el impuesto no la confirma: en los 13 registros negativos, el tax siempre es el 21% del valor absoluto del subtotal, un patrón compatible tanto con créditos como con un cambio de signo. Si las enviáramos a Quarantine, el gasto neto mensual quedaría inflado y FinOps estaría tomando decisiones sobre números incorrectos; además, el diseño no corrige los datos en cuarentena, así que quedarían afuera de los totales.

## Por qué los costos negativos de usage_events_stream sí van a Quarantine

En usage_events_stream encontramos cost_usd_increment con valores hasta -154.46. A diferencia de billing, acá no tiene sentido de negocio: un recurso de nube no puede generar un consumo físico negativo. Por eso se tratan como anomalías y se envían a Quarantine.

## Por qué se particiona por year/month

Decidimos particionar los eventos solo por year/month, que deja 2 carpetas de 20.880 y 22.320 eventos, y no particionar las tablas CSV porque tienen pocas filas.  por que la partición por year/month sirve para procesar y reprocesar los datos por período;  donde las consultas por organización las hacen FinOps, Soporte y Producto sobre Cassandra/AstraDB, no sobre los archivos del data lake.

## Por qué los nulos de carbon_kg no van a Quarantine

En la exploración se verificó que los 10.800 registros con carbon_kg nulo coinciden exactamente con los registros de schema_version = 1. Eso indica que es una evolución del esquema y no un error aleatorio: la versión 1 simplemente no incluía ese campo. Mandarlos a Quarantine eliminaría una cuarta parte del historial de eventos sin razón válida.

## Por qué se usa Parquet y no CSV en Bronze, Silver y Gold

Por que parquet guarda los datos por columnas y comprimidos.Si PySpark necesita solo algunos campos, lee solo esas columnas sin abrir el archivo completo. Con 43.200 eventos y múltiples tablas, esto hace el procesamiento más rápido y ocupa menos espacio que CSV.

## Por qué el watermark es de 10 minutos
Decidimos usar un watermark de 10 minutos sobre el campo timestamp de usage_events_stream, y ordenar los eventos por timestamp antes de enviarlos al stream. El watermark le dice a Spark hasta cuándo esperar eventos que llegan tarde. Elegimos 10 minutos porque es un valor intermedio para que el sistema funcione de forma continua, ya que los eventos llegarían casi en orden: con 1 hora Spark guardaría en memoria eventos de la última hora sin necesidad, y con 1 minuto correríamos el riesgo de descartar eventos válidos que llegaron un poco tarde. El orden previo es necesario porque los 120 archivos no están ordenados cronológicamente: cada uno abarca casi todo el rango, y si los procesáramos tal como están, cerca del 98,32 % de los eventos se marcaría como tardío.

## Por qué la tabla de Cassandra guarda juntas las filas de cada organización
Tomamos la decison de que la tabla org_daily_usage_by_service en Cassandra tenga como clave primaria ((org_id), usage_date, service). Esto hace que Cassandra guarde juntas todas las filas de una organización, ordenadas por fecha y después por servicio. Lo elegimos porque FinOps, Soporte y Producto siempre consultan una organización en un período, y con esta clave la consulta lee solo los datos de esa organización y filtra el rango de fechas. Además, el servicio forma parte de la clave para que dos servicios de la misma organización en el mismo día no se pisen entre sí. Esta clave hace que Cassandra no pueda agrupar solo por servicio, por eso la suma de costos por servicio de la consulta 2 se hace en Python para que despues se puedan leer los datos.

## Por qué los eventos sin unit no van a Quarantine
Decidimos completar el campo unit en los eventos que lo traen vacío y no enviarlos a Quarantine. En los datos pudimos ver que cada métrica siempre usa la misma unidad: requests es count, cpu_hours es hours y storage_gb_hours es gb_hours. Por lo que con esa base asumimos que los eventos sin unidad usan la misma que el resto de su métrica y dejamos la marca unit_imputed para saber cuáles se completaron. Esto es una suposición que sale de los datos, no de una especificación del proveedor. Ademas si los enviáramos a Quarantine juntos con los costos negativos quedaría afuera el 5,28 % de los eventos y no cumpliríamos el objetivo de habiamos definidos de menos del 5 %.
