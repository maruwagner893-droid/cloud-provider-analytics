# Pruebas del pipeline (se corren después del notebook 02)
# Desde la carpeta del repositorio:  python tests/test_pipeline.py

import json, os, shutil, sys
from datetime import datetime, timedelta

import yaml
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

sys.path.append(".")
from src.gold import calcular_gold

config = yaml.safe_load(open("config/pipeline.yml", encoding="utf-8"))
RUTAS = config["rutas"]

spark = (SparkSession.builder
         .appName("pruebas")
         .config("spark.sql.shuffle.partitions", config["spark"]["shuffle_partitions"])
         .getOrCreate())
spark.conf.set("spark.sql.session.timeZone", config["spark"]["timezone"])
spark.sparkContext.setLogLevel("ERROR")   # solo mostrar errores, no los avisos de Spark
fallas = 0

def revisar(texto, valor, esperado):
    global fallas
    print(texto, valor)
    if valor != esperado:
        print("   FALLA: se esperaba", esperado)
        fallas += 1

# 1) Bronze
bronze = spark.read.parquet(RUTAS["bronze_eventos"])
revisar("Bronze:", bronze.count(), 43200)
revisar("event_id distintos en Bronze:", bronze.select("event_id").distinct().count(), 43200)
revisar("Bronze sin ingest_ts o source_file:",
        bronze.filter(F.col("ingest_ts").isNull() | F.col("source_file").isNull()).count(), 0)

# 2) Silver y Quarantine
silver = spark.read.parquet(RUTAS["silver_eventos"])
quarantine = spark.read.parquet(RUTAS["quarantine_eventos"])
revisar("Silver:", silver.count(), 42989)
revisar("Quarantine:", quarantine.count(), 211)
revisar("event_id nulos en Silver:", silver.filter(F.col("event_id").isNull()).count(), 0)
revisar("costos menores al mínimo en Silver:",
        silver.filter(F.col("cost_usd_increment") < config["calidad"]["costo_minimo"]).count(), 0)
revisar("unit nulos en Silver:", silver.filter(F.col("unit").isNull()).count(), 0)
revisar("Quarantine sin motivo:", quarantine.filter(F.col("quarantine_reason").isNull()).count(), 0)
revisar("Silver billing:", spark.read.parquet(RUTAS["silver_billing"]).count(), 240)
tickets = spark.read.parquet(RUTAS["silver_tickets"])
bronze_tickets = spark.read.parquet(os.path.join(RUTAS["bronze"], "support_tickets"))
revisar("Silver tickets:", tickets.count(), 1000)
revisar("Tickets abiertos:", tickets.filter("is_open").count(), 240)
revisar("Tickets sin organización:", tickets.filter(F.col("industry").isNull()).count(), 0)
revisar("Tickets en cuarentena (Bronze - Silver):", bronze_tickets.count() - tickets.count(), 0)

# 3) Gold
gold = spark.read.parquet(RUTAS["gold_uso"])
revisar("Gold:", gold.count(), 11050)
revisar("Claves únicas en Gold:", gold.select("org_id", "usage_date", "service").distinct().count(), 11050)
revisar("Suma n_events en Gold:", gold.agg(F.sum("n_events")).first()[0], 42989)
revisar("Filas del mart de anomalías:", spark.read.parquet(RUTAS["gold_anomalias"]).count(), 11050)

# 4) Gold saca los repetidos que llegan tarde
repetidos = silver.filter(F.col("org_id") == "org_xaji0y6d")
gold_prueba = calcular_gold(silver.union(repetidos))
revisar("Gold con repetidos:", gold_prueba.count(), 11050)
revisar("Suma n_events con repetidos:", gold_prueba.agg(F.sum("n_events")).first()[0], 42989)

# 5) Watermark sobre ingest_ts: el evento tardío entra y el repetido se saca
ENTRADA, CHECKPOINT = "data/test_pruebas/in", "data/test_pruebas/checkpoint"
shutil.rmtree("data/test_pruebas", ignore_errors=True)
os.makedirs(ENTRADA, exist_ok=True); os.makedirs(CHECKPOINT, exist_ok=True)

ESQUEMA = "event_id STRING, `timestamp` TIMESTAMP, org_id STRING, service STRING, cost_usd_increment DOUBLE"

def escribir_eventos(nombre, eventos):
    with open(f"{ENTRADA}/{nombre}.json", "w", encoding="utf-8") as f:
        for event_id, ts in eventos:
            f.write(json.dumps({"event_id": event_id, "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                                "org_id": "org_test", "service": "compute", "cost_usd_increment": 0.1}) + "\n")

consulta = (spark.readStream.schema(ESQUEMA).json(ENTRADA)
            .withColumn("ingest_ts", F.current_timestamp())
            .withWatermark("ingest_ts", config["streaming"]["watermark"])
            .dropDuplicatesWithinWatermark(["event_id"])
            .writeStream.format("memory").queryName("prueba_ingest").outputMode("append")
            .option("checkpointLocation", CHECKPOINT)
            .trigger(processingTime="2 seconds")
            .start())

t0 = datetime(2025, 8, 1, 10, 0)
escribir_eventos("lote_001", [("t1", t0), ("t2", t0 + timedelta(minutes=5))])
consulta.processAllAvailable()
escribir_eventos("lote_002", [("t3", t0 + timedelta(minutes=30))])
consulta.processAllAvailable()
escribir_eventos("lote_003", [("t4", t0 + timedelta(minutes=2)), ("t1", t0)])   # t4 tardío, t1 repetido
consulta.processAllAvailable()

prueba = spark.sql("SELECT * FROM prueba_ingest")
revisar("Eventos que entraron:", prueba.count(), 4)                              # t1, t2, t3 y t4
revisar("event_id distintos:", prueba.select("event_id").distinct().count(), 4)  # t4 no se descartó
consulta.stop()

# 6) Idempotencia: volver a ejecutar o recibir un archivo repetido no suma eventos
SALIDA, CHECKPOINT = "data/test_pruebas/salida", "data/test_pruebas/checkpoint_idem"
shutil.rmtree(ENTRADA, ignore_errors=True)
os.makedirs(ENTRADA, exist_ok=True)
escribir_eventos("lote_001", [("i1", t0), ("i2", t0), ("i3", t0)])

def ejecutar():
    (spark.readStream.schema(ESQUEMA).json(ENTRADA)
     .withColumn("ingest_ts", F.current_timestamp())
     .withWatermark("ingest_ts", config["streaming"]["watermark"])
     .dropDuplicatesWithinWatermark(["event_id"])
     .writeStream.format("parquet").outputMode("append")
     .option("path", SALIDA)
     .option("checkpointLocation", CHECKPOINT)
     .trigger(availableNow=True)
     .start().awaitTermination())
    return spark.read.parquet(SALIDA).count()

revisar("Primera ejecución:", ejecutar(), 3)
revisar("Sin archivos nuevos:", ejecutar(), 3)
escribir_eventos("lote_001_repetido", [("i1", t0), ("i2", t0), ("i3", t0)])
revisar("Con un archivo repetido:", ejecutar(), 3)
shutil.rmtree("data/test_pruebas", ignore_errors=True)

print()
if fallas == 0:
    print("Todas las pruebas pasaron")
else:
    print("Pruebas con falla:", fallas)
    sys.exit(1)
