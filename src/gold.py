# Cálculo de Gold: org_daily_usage_by_service
# Lo usan el notebook 02 y las pruebas de tests/

from pyspark.sql import functions as F


def calcular_gold(silver):
    # Reconciliación batch: se calcula con todo Silver y saca los repetidos
    # que hayan llegado después del watermark de Bronze
    return (
        silver
        .dropDuplicates(["event_id"])
        .groupBy("org_id", "usage_date", "service")
        .agg(
            F.round(F.sum("cost_usd_increment"), 4).alias("daily_cost_usd"),
            F.sum("requests").alias("requests"),
            F.sum("cpu_hours").alias("cpu_hours"),
            F.sum("storage_gb_hours").alias("storage_gb_hours"),
            F.sum("genai_tokens").alias("genai_tokens"),
            F.sum("carbon_kg").alias("carbon_kg"),
            F.count("*").alias("n_events"),
        )
        .withColumn("year", F.year("usage_date"))
        .withColumn("month", F.month("usage_date"))
    )
