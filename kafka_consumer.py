from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import time
import os

# Global batch counter
batch_id_accumulator = {"count": 0}

def custom_write_to_csv(batch_df, batch_id):
    # Increment batch counter
    batch_id_accumulator["count"] += 1
    file_name = f"file_{batch_id_accumulator['count']}.csv"
    output_path = os.path.join(output_dir, file_name)

    # Write DataFrame to single CSV file (you can repartition to 1 if needed)
    batch_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_path)

def start_spark_streaming_app(bootstrap_servers, topic_name, output_dir_path):
    global output_dir
    output_dir = output_dir_path  # So custom_write_to_csv can access it

    spark = SparkSession.builder \
        .appName("KafkaToCSVStreaming") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", bootstrap_servers) \
        .option("subscribe", topic_name) \
        .option("startingOffsets", "earliest") \
        .load()

    messages_df = kafka_df.selectExpr("CAST(value AS STRING) as message")

    query = messages_df.writeStream \
        .foreachBatch(custom_write_to_csv) \
        .outputMode("append") \
        .trigger(processingTime="10 seconds") \
        .option("checkpointLocation", output_dir + "_checkpoint") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    bootstrap_servers = "kafka-1:9092,kafka-2:9093,kafka-3:9094"
    topic_name = "second_test"
    output_dir = "./messages"

    time.sleep(5)
    start_spark_streaming_app(bootstrap_servers, topic_name, output_dir)
