from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import time
import os

def load_counter(counter_file):
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as f:
            data = json.load(f)
            return data
            return data.get("count", 0)
    return 0

def save_counter(count):
    with open(counter_file, 'w') as f:
        json.dump({"count": count}, f)

def custom_write_to_csv(batch_df, batch_id):
    # Increment batch counter
    batch_file = load_counter(counter_file)
    batch_file["count"] += 1
    save_counter(batch_file["count"])
    file_name = f"file_{batch_file['count']}.csv"
    output_path = os.path.join(output_dir, file_name)

    # Write DataFrame to single CSV file (you can repartition to 1 if needed)
    batch_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_path)

def start_spark_streaming_app(bootstrap_servers, 
    topic_name, output_dir_path, counter_json_file):
    global output_dir
    global counter_file
    output_dir = output_dir_path  # So custom_write_to_csv can access it
    counter_file = counter_json_file

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
    counter_file = "batch_counter.json"

    time.sleep(5)
    start_spark_streaming_app(bootstrap_servers, 
        topic_name, output_dir, counter_file)
