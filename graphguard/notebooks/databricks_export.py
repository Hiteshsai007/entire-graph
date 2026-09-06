# Databricks notebook source
"""Materialize uploaded GraphGuard reports as Delta tables and MLflow metrics."""

# COMMAND ----------

from time import perf_counter

import mlflow
from delta.tables import DeltaTable
from pyspark.sql import functions as F

CATALOG = "workspace"  # Replace with your Unity Catalog name.
SCHEMA = "graphguard"
VOLUME = "input"
EXPERIMENT = "/Shared/graphguard"

VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/graphguard/reports"
TABLE_PREFIX = f"{CATALOG}.{SCHEMA}"

# COMMAND ----------

started = perf_counter()
raw = spark.read.option("multiLine", "true").json(f"{VOLUME_PATH}/report-*.json")

if "verification" not in raw.columns:
    raw = raw.withColumn(
        "verification",
        F.lit(None).cast(
            "struct<status:string,baseline_passed:boolean,post_edit_passed:boolean,"
            "baseline_output:string,post_edit_output:string,detail:string>"
        ),
    )

impact_reports = raw.select(
    "report_id", "timestamp", "symbol", "repo", "tier", "rule_id", "reason",
    F.col("facts.file_path").alias("file_path"),
    F.col("facts.line").cast("int").alias("line"),
    F.col("facts.direct_callers").cast("int").alias("direct_callers"),
    F.col("facts.transitive_callers").cast("int").alias("transitive_callers"),
    F.col("facts.reachable_tests").cast("int").alias("reachable_tests"),
    F.col("facts.cochange_files").cast("int").alias("cochange_files"),
)

impact_evidence = (
    raw.select("report_id", F.explode_outer("evidence").alias("e"))
    .select(
        "report_id", F.col("e.tag").alias("tag"), F.col("e.content").alias("content"),
        F.col("e.file_line").alias("file_line"), F.col("e.argv").alias("argv"),
    )
    .withColumn("evidence_id", F.sha2(F.concat_ws("||", "report_id", "tag", "content", "file_line", "argv"), 256))
)

test_recommendations = (
    raw.select("report_id", F.explode_outer("ranked_tests").alias("t"))
    .select(
        "report_id", F.col("t.test_name").alias("test_name"),
        F.col("t.score").cast("int").alias("score"), F.col("t.reason").alias("reason"),
        F.col("t.path").alias("graph_path"),
    )
    .withColumn("recommendation_id", F.sha2(F.concat_ws("||", "report_id", "test_name", "score", "reason", "graph_path"), 256))
)

verification_runs = raw.filter(F.col("verification").isNotNull()).select(
    "report_id", F.col("verification.status").alias("status"),
    F.col("verification.baseline_passed").alias("baseline_passed"),
    F.col("verification.post_edit_passed").alias("post_edit_passed"),
    F.col("verification.detail").alias("detail"),
)


def upsert(dataframe, table_name, key):
    if dataframe.limit(1).count() == 0:
        return
    if not spark.catalog.tableExists(table_name):
        dataframe.write.format("delta").mode("overwrite").saveAsTable(table_name)
        return
    (
        DeltaTable.forName(spark, table_name).alias("target")
        .merge(dataframe.alias("source"), f"target.{key} = source.{key}")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )


upsert(impact_reports, f"{TABLE_PREFIX}.impact_reports", "report_id")
upsert(impact_evidence, f"{TABLE_PREFIX}.impact_evidence", "evidence_id")
upsert(test_recommendations, f"{TABLE_PREFIX}.test_recommendations", "recommendation_id")
upsert(verification_runs, f"{TABLE_PREFIX}.verification_runs", "report_id")

# COMMAND ----------

mlflow.set_experiment(EXPERIMENT)
with mlflow.start_run(run_name="graphguard-json-export"):
    mlflow.set_tags({"graphguard.decision_engine": "deterministic", "graphguard.grounding": "entire_graph"})
    mlflow.log_metric("impact_reports", impact_reports.count())
    mlflow.log_metric("evidence_rows", impact_evidence.count())
    mlflow.log_metric("test_recommendations", test_recommendations.count())
    mlflow.log_metric("verification_runs", verification_runs.count())
    for row in impact_reports.groupBy("tier").count().collect():
        mlflow.log_metric(f"tier_{row['tier'].lower()}_count", row["count"])
    for row in verification_runs.groupBy("status").count().collect():
        mlflow.log_metric(f"outcome_{row['status'].lower().replace(' ', '_')}_count", row["count"])
    mlflow.log_metric("export_seconds", perf_counter() - started)

print("GraphGuard export complete.")
