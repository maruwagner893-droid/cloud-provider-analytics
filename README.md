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
├── data/
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
│   └── Exploración y análisis de datos
│
├── src/
│   └── Pipelines y transformaciones en PySpark
│
└── evidence/
    └── Evidencias, capturas y registro de decisiones
```

## Data Lake
- **Landing:** recepción inicial de datos.
- **Bronze:** almacenamiento de datos crudos.
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
1. Clonar el repositorio
2. Copiar `cloud_provider_challenge_dataset_v1.zip` en la carpeta `data/`
3. Instalar dependencias: `pip install -r requirements.txt`
4. Abrir `notebooks/Exploracion_Cloud_Provider_Analytics.ipynb` y ejecutar todas las celdas
