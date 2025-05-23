import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType

kafka_brokers = os.environ.get("KAFKA_BROKERS", "kafka1:29092").split(",")

spark = SparkSession.builder \
    .appName("KafkaSparkConsumer") \
    .getOrCreate()

schema = StructType() \
    .add("id", StringType()) \
    .add("name", StringType()) \
    .add("text_message", StringType())

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", "user-messages") \
    .option("startingOffsets", "latest") \
    .load()

parsed = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

query = parsed.writeStream \
    .format("csv") \
    .option("path", "./output/") \
    .option("checkpointLocation", "./chkpt/") \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()
