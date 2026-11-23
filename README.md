# Cloud Provider Analytics

## Proyecto integrador de Minería de Datos II (ISTEA, 2C 2026)

## Contexto
Los datos generados por los clientes del proveedor cloud (uso de servicios, facturación, tickets de soporte, entre otros) llegan en formatos que contienen errores, valores nulos e inconsistencias.
El objetivo del proyecto es construir un pipeline de datos que permita limpiar, validar, transformar y disponibilizar esta información de forma confiable para los distintos equipos de negocio.

## Objetivo
Automatizar el procesamiento de datos y la generación de información analítica para reducir tareas manuales, mejorar la calidad de los datos y ofrecer información actualizada tanto para análisis operativos como estratégicos.

Los objetivos específicos son:
- Reducir el tiempo de generación de reportes de horas a minutos.
- Reducir la tasa de registros inválidos por debajo del 5% del total procesado.
- Poner la información disponible en menos de 30 minutos desde que llegan los datos.
- Entregar métricas con una latencia máxima de 60 segundos desde la llegada del evento.

## Arquitectura
La solución implementa una Arquitectura Lambda que combina:
- Procesamiento Batch para información histórica.
- Procesamiento Streaming para eventos en tiempo real.
- Capa de consumo(Cassandra/AstraDB) para métricas y visualizaciones.

## Estructura del Repositorio

```
cloud-provider-analytics/
│
├── config/
│   └── pipeline.yml: rutas y parámetros del pipeline
│
├── data/  
│   ├── cloud_provider_challenge_dataset_v1.zip  
│   ├── landing/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── quarantine/
│
├── docs/
│   └── Documentación y diseño de la solución
│
├── notebooks/
│   └── Exploración de datos y pipeline de la etapa 2
│
├── src/
│   └── Cálculo de Gold (gold.py) y script CQL de la capa de Serving
│
├── tests/
│   └── Pruebas automáticas del pipeline (test_pipeline.py)
│
└── evidence/
    └── Evidencias, capturas y registro de decisiones
```

## Data Lake
- **Landing:** recepción inicial de datos.
- **Bronze:** datos tipificados, sin duplicados y con metadatos de ingesta como:ingest_ts y source_file.
- **Silver:** datos limpios y estandarizados.
- **Gold:** métricas y datasets de negocio.
- **Quarantine:** registros invalidos por problemas de calidad.

## Tecnologías
- Python
- PySpark
- Apache Spark
- Arquitectura Lambda
- Data Lake
- Cassandra/AstraDB, que es la capa de Serving

## Áreas Beneficiadas
- FinOps (Financial Operations): controla y optimiza los costos del uso de la nube.
- Soporte: gestiona los tickets de soporte de los clientes. 
- Producto: analiza cómo los clientes usan los servicios (qué recursos usan, cuánto, con qué frecuencia). También ve métricas de NPS (satisfacción del cliente).

## Documentación
La documentación detallada de diseño se encuentra en: `docs/`

## Evidencias
Capturas de pantalla, validaciones y decisiones tomadas durante el desarrollo: `evidence/`

## Cómo ejecutar
Se necesita Python 3, una cuenta de Google para Colab y una cuenta de Astra DB.

1. Clonar el repositorio: https://github.com/maruwagner893-droid/cloud-provider-analytics. el dataset ya está en la carpeta data/.

### Etapa 1: exploración de datos
2. Dentro de la carpeta del repositorio, instalar las dependencias con: pip install -r requirements.txt
3. Abrir notebooks/Exploracion_Cloud_Provider_Analytics.ipynb con Jupyter (o con VS Code) y ejecutar todas las celdas. El notebook descomprime el dataset de data/ y no necesita Spark ni Astra.

### Etapa 2: pipeline
4. Abrir notebooks/02_pipeline_etapa2.ipynb en Google Colab,con este enlace: https://colab.research.google.com/github/maruwagner893-droid/cloud-provider-analytics/blob/main/notebooks/02_pipeline_etapa2.ipynb .Tener encuenta que en sus primeras celdas el notebook vuelve a clonar el repositorio dentro de Colab y descomprime el dataset, por lo cual que no hace falta subir nada a mano.
5. Para Cassandra, antes de ejecutar:
 - Crear una base de datos en Astra DB:astra.datastax.com y, desde el portal, agregar un keyspace con el nombre cloud_provider
- Generar un token con el rol Database Administrator y descargar el secure connect bundle de la base, sin cambiarle el nombre
- Subir el secure connect bundle a /content/ en Colab y guardar el token en los Secretos de Colab con el nombre ASTRA_TOKEN, activando el acceso del notebook
6. Desde el menú Entorno de ejecución, elegir Ejecutar todas. El notebook tarda varios minutos. La última celda corre las pruebas automáticas y tiene que terminar con: Todas las pruebas pasaron. Las rutas y los parámetros:watermark, archivos por micro-lote, regla de costo y keyspace, se leen de config/pipeline.yml.
7. Si Colab se reinicia, hay que volver a subir el bundle a /content/, porque esa carpeta se borra.
 
## Pruebas
Las pruebas que hicimos con:idempotencia, archivos desordenados, datos tardíos y conteos de cada capa, que están descritas en docs/pruebas_y_reproducibilidad.md, y sus resultados en las salidas del notebook y en la carpeta evidence/.

## Limitaciones
- El watermark de Bronze va sobre ingest_ts y no sobre timestamp, porque con los archivos como vienen el watermark sobre timestamp descarta el 98,3 % de los eventos. Por eso Bronze no descarta eventos por su fecha y los tardíos se corrigen cuando Gold se vuelve a calcular en batch.
- La consulta 2 suma los costos por servicio en Python, porque la tabla de Cassandra no permite agrupar solo por servicio.
