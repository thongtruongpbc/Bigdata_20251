import os
import base64
import pandas as pd
import numpy as np
import cv2
from datetime import timedelta
from ultralytics import YOLO
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window
from pyspark.sql.types import StructType, StringType, TimestampType
from feast import FeatureStore
from minio_utils import upload_to_minio
import logging

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Config YOLO & congestion logic
model_yolo = None

def get_model():
    global model_yolo
    if model_yolo is None:
        model_yolo = YOLO("yolov8n.pt", device='cpu')
    return model_yolo

CONGESTION_THRESHOLD = 50
TARGET_CLASSES = [2, 3, 5, 7]  
conf_counting = 0.5
conf_storage = 0.75

# def process_ai_logic(row):
#     try:
#         model = get_model()
#         img_bytes = base64.b64decode(row["image_data"])
#         nparr = np.frombuffer(img_bytes, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#         if img is None:
#             return 0, 0

#         results = model(img, verbose=False, conf=conf_counting)[0]
#         classes = results.boxes.cls.cpu().numpy()
#         confs = results.boxes.conf.cpu().numpy()
#         target_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck

#         vehicle_indices = [i for i, c in enumerate(classes) if int(c) in target_classes]
#         vehicle_count = len(vehicle_indices)

#         # Upload only confident boxes
#         boxes_storage = [results.boxes[i] for i in vehicle_indices if confs[i] >= conf_storage]
#         if boxes_storage:
#             upload_to_minio(img, boxes_storage, row["id_camera"], row["timestamp"])

#         is_congested = 1 if vehicle_count > CONGESTION_THRESHOLD else 0
#         return vehicle_count, is_congested
#     except Exception as e:
#         print("Error processing image:", e)
#         return 0, 0

# # def process_ai_logic(row):
# #     # stub logic – thay bằng ONNX sau
# #     vehicle_count = 0
# #     is_congested = 0
# #     return vehicle_count, is_congested


# def preprocess_fn(pdf: pd.DataFrame) -> pd.DataFrame:
#     if pdf.empty:
#         return pdf

#     res = pdf.apply(process_ai_logic, axis=1)
#     pdf["vehicle_count"] = res.apply(lambda x: x[0]).astype(int)
#     pdf["is_congested"] = res.apply(lambda x: x[1]).astype(int)
#     pdf["timestamp"] = pd.to_datetime(pdf["timestamp"])
#     return pdf[["id_camera", "timestamp", "vehicle_count", "is_congested"]]

# # -----------------------------
# # Spark session
# # -----------------------------
# os.environ["PYSPARK_SUBMIT_ARGS"] = "--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 pyspark-shell"
# spark = (
#     SparkSession.builder
#     .master("local[1]")
#     .appName("camera-ai-processor")
#     .config("spark.driver.memory", "512m")
#     .config("spark.sql.execution.arrow.pyspark.enabled", "true")
#     .getOrCreate()
# )
# # spark.sparkContext.setLogLevel("INFO")

# # -----------------------------
# # Feast feature store
# # -----------------------------
# repo_path = "../../feature_repo"
# store = FeatureStore(repo_path=repo_path)

# sfv = store.get_stream_feature_view("camera_stats_stream")

# # -----------------------------
# # Kafka stream setup
# # -----------------------------
# kafka_topic = "camera_stream"
# kafka_servers = "localhost:9092"


# schema = StructType() \
#     .add("id_camera", StringType()) \
#     .add("timestamp", TimestampType()) \
#     .add("image_data", StringType())

# df_raw = (
#     spark.readStream.format("kafka")
#     .option("kafka.bootstrap.servers", kafka_servers)
#     .option("subscribe", kafka_topic)
#     .option("startingOffsets", "latest")
#     .load()
# )

# df_parsed = df_raw.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

# # -----------------------------
# # Apply AI logic using Pandas UDF
# # -----------------------------
# df_result = df_parsed.mapInPandas(preprocess_fn, schema="id_camera string, timestamp timestamp, vehicle_count int, is_congested int")

# # -----------------------------
# # Write stream to console (or offline store)
# # -----------------------------
# query = (
#     df_result.writeStream
#     .outputMode("append")
#     .format("parquet").option("path", "/tmp/feast_camera")
#     .option("truncate", False)
#     .option("checkpointLocation", "/tmp/feast_camera_checkpoint") \
#     .start()
# )

# query.awaitTermination()

# #sudo sync
# # sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

print('hello')
# def process_ai_logic(row):
#     try:
#         logger.info(f"Processing image from camera {row['id_camera']} at {row['timestamp']}")
#         model = get_model()
#         img_bytes = base64.b64decode(row["image_data"])
#         nparr = np.frombuffer(img_bytes, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#         if img is None:
#             return 0, 0

#         img = cv2.resize(img, (320, 320))

#         results = model(img, verbose=False, conf=conf_counting)[0]
#         classes = results.boxes.cls.cpu().numpy()
#         confs = results.boxes.conf.cpu().numpy()

#         vehicle_indices = [i for i, c in enumerate(classes) if int(c) in TARGET_CLASSES]
#         vehicle_count = len(vehicle_indices)

#         # Upload only confident boxes
#         boxes_storage = [results.boxes[i] for i in vehicle_indices if confs[i] >= conf_storage]
#         if boxes_storage:
#             upload_to_minio(img, boxes_storage, row["id_camera"], row["timestamp"])

#         is_congested = 1 if vehicle_count > CONGESTION_THRESHOLD else 0
#         del img, nparr, results, classes, confs, boxes_storage
#         return vehicle_count, is_congested
#     except Exception as e:
#         print("Error processing image:", e)
#         return 0, 0

def process_ai_logic(row):
    logger.info(f"Received row from {row['id_camera']}")
    return np.random.randint(0, 10), np.random.randint(0, 2)

# Spark session

os.environ["PYSPARK_SUBMIT_ARGS"] = "--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 pyspark-shell"
spark = SparkSession.builder \
    .master("local[1]") \
    .appName("camera-ai-processor") \
    .config("spark.driver.memory", "512m") \
    .getOrCreate()

logger.info("Processor started. Waiting for Kafka messages...")


# Feast feature store
repo_path = "../../feature_repo"
store = FeatureStore(repo_path=repo_path)
sfv = store.get_stream_feature_view("camera_stats_stream")

# Kafka stream setup
kafka_topic = "camera_stream"
kafka_servers = "localhost:29092"

schema = StructType() \
    .add("id_camera", StringType()) \
    .add("timestamp", TimestampType()) \
    .add("image_data", StringType())

df_raw = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", kafka_servers)
    .option("subscribe", kafka_topic)
    .option("startingOffsets", "earliest")
    .load()
)

df_parsed = df_raw.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

# Xử lý batch streaming
def process_batch(df, batch_id):
    count = df.count()
    logger.info(f"Batch {batch_id} received {count} rows")
    if count == 0:
        return
    rows = df.collect()  # mỗi row là 1 frame
    results = []
    logger.info(f"Processing batch with {len(rows)} rows")
    for row in rows:
        
        vehicle_count, is_congested = process_ai_logic(row.asDict())
        results.append((row["id_camera"], row["timestamp"], vehicle_count, is_congested))
    del rows
    if results:
        # Parquet / Feast offline store
        import pandas as pd
        batch_df = pd.DataFrame(results, columns=["id_camera", "timestamp", "vehicle_count", "is_congested"])
        batch_df.to_parquet(f"/vscode/feast_camera/batch_{batch_id}.parquet", index=False)
        print(f"Batch {batch_id} processed, {len(results)} rows")

query = (
    df_parsed.writeStream
    .foreachBatch(process_batch)
    .outputMode("append")
    .format("console")
    .option("checkpointLocation", "/vscode/feast_camera_checkpoint")
    .config("spark.sql.execution.arrow.pyspark.enabled", "false")
    .start()
)

query.awaitTermination()