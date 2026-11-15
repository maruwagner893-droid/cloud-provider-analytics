# Pruebas y reproducibilidad

## Puesta en marcha
Los pasos para poder ejecutar el proyecto desde cero están en la sección Cómo ejecutar del README. Al ejecutarse, el notebook notebooks/02_pipeline_etapa2.ipynb clona el repositorio, descomprime el dataset de data/ e instala PySpark y cassandra-driver de forma automática. Lo que si se tiene que preparar a mano es la conexión a Cassandra: crear la base en Astra DB con el keyspace cloud_provider, generar el token y descargar el secure connect bundle, y después, en Colab, guardar el token en los Secretos con el nombre ASTRA_TOKEN y subir el bundle a /content/.
Ademas las versiones de las dependencias están en requirements.txt. La última ejecución completa se hizo con Spark 4.0.5 en Google Colab.

## Logs

## Manejo de errores

## Pruebas
