
# Decisiones de diseño

## Por qué Lambda y no Kappa

Kappa solo utiliza procesamiento en tiempo real (streaming), con un único camino para todos los datos. En este proyecto la mayoría de las fuentes son archivos CSV que llegan periódicamente (billing, tickets, usuarios, etc.), no en tiempo real. Usar Kappa obligaría a procesar esos datos como si fueran un stream cuando no lo son. Lambda permite tener un camino batch para los CSV y un camino streaming solo para usage_events_stream, que es la única fuente que llega en tiempo real.

## Por qué los costos negativos de billing_monthly no van a Quarantine

En billing_monthly encontramos 13 facturas con subtotal negativo, la más baja es de -1671.83. Decidimos mantenerlas en el pipeline marcadas como créditos y no enviarlas a Quarantine. Probablemente son créditos del proveedor de nube, como devoluciones o ajustes por compromisos de uso, y lo que apoya esa hipótesis es el impuesto, donde en los 13 registros negativos, el tax siempre es el 21% del valor absoluto del subtotal. Si las enviáramos a Quarantine, el gasto neto mensual quedaría inflado y FinOps estaría tomando decisiones sobre números incorrectos; además, el diseño no corrige los datos en cuarentena, así que quedarían afuera de los totales.

## Por qué los costos negativos de usage_events_stream sí van a Quarantine

En usage_events_stream encontramos cost_usd_increment con valores hasta -154.46. A diferencia de billing, acá no tiene sentido de negocio: un recurso de nube no puede generar un consumo físico negativo. Por eso se tratan como anomalías y se envían a Quarantine.

## Por qué se particiona por year/month/org_id

Las tres áreas  siempre consultan filtrando por organización y por período de tiempo. Con esa estructura de carpetas, PySpark va directo a la carpeta que corresponde sin necesidad de leer el dataset completo. En un escenario de producción con miles de organizaciones, esto reduce significativamente el tiempo de procesamiento.

## Por qué los nulos de carbon_kg no van a Quarantine

En la exploración se verificó que los 10.800 registros con carbon_kg nulo coinciden exactamente con los registros de schema_version = 1. Eso indica que es una evolución del esquema y no un error aleatorio: la versión 1 simplemente no incluía ese campo. Mandarlos a Quarantine eliminaría una cuarta parte del historial de eventos sin razón válida.

## Por qué se usa Parquet y no CSV en Bronze, Silver y Gold

Por que parquet guarda los datos por columnas y comprimidos.Si PySpark necesita solo algunos campos, lee solo esas columnas sin abrir el archivo completo. Con 43.200 eventos y múltiples tablas, esto hace el procesamiento más rápido y ocupa menos espacio que CSV.

## Por qué el watermark es de 10 minutos
Decidimos usar un watermark de 10 minutos sobre el campo timestamp de usage_events_stream, y ordenar los eventos por timestamp antes de enviarlos al stream. El watermark le dice a Spark hasta cuándo esperar eventos que llegan tarde. Elegimos 10 minutos porque es un valor intermedio para que el sistema funcione de forma continua, ya que los eventos llegarían casi en orden: con 1 hora Spark guardaría en memoria eventos de la última hora sin necesidad, y con 1 minuto correríamos el riesgo de descartar eventos válidos que llegaron un poco tarde. El orden previo es necesario porque los 120 archivos no están ordenados cronológicamente: cada uno abarca casi todo el rango, y si los procesáramos tal como están, cerca del 99,1 % de los eventos se marcaría como tardío.
