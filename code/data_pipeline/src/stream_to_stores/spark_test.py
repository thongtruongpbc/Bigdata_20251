from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, TimestampType
import psutil
import threading
import sys
import time

# --- Cấu hình giám sát RAM ---
RAM_THRESHOLD_PERCENT = 90 
CHECK_INTERVAL = 5           # giây

def monitor_ram(spark_session):
    """Thread giám sát RAM, dừng Spark nếu quá ngưỡng"""
    while True:
        mem = psutil.virtual_memory()
        used_percent = mem.percent
        if used_percent >= RAM_THRESHOLD_PERCENT:
            print(f"[WARNING] RAM usage {used_percent}% >= {RAM_THRESHOLD_PERCENT}%, stopping Spark...")
            spark_session.stop()
            sys.exit(1)
        # print(f"RAM usage: {used_percent}%")
        time.sleep(CHECK_INTERVAL)

# --- Khởi tạo Spark ---
spark = SparkSession.builder \
    .master("local[1]") \
    .appName("test_kafka") \
    .config("spark.driver.memory", "512m") \
    .config("spark.executor.memory", "512m") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1") \
    .getOrCreate()

print("Spark version:", spark.version)

ram_thread = threading.Thread(target=monitor_ram, args=(spark,), daemon=True)
ram_thread.start()

# --- Định nghĩa schema Kafka message ---
schema = StructType() \
    .add("id_camera", StringType()) \
    .add("timestamp", TimestampType()) \
    .add("image_data", StringType())

# --- Đọc dữ liệu Kafka streaming ---
df_raw = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:29092") \
    .option("subscribe", "camera_stream") \
    .option("startingOffsets", "earliest") \
    .load()

df_parsed = df_raw.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

query = df_parsed.writeStream.format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
