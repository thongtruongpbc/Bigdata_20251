import pandas as pd
import pyspark.sql.functions as F
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[1]").appName("test_batch").getOrCreate()

data = [
    {"id_camera": "cam_001", "timestamp": "2026-01-12T18:30:00", "image_data": "BASE64_STRING"},
    {"id_camera": "cam_002", "timestamp": "2026-01-12T18:31:00", "image_data": "BASE64_STRING"},
]

pdf = pd.DataFrame(data)
df = spark.createDataFrame(pdf)

def process_batch_test(df, batch_id):
    rows = df.collect()
    print(f"Batch {batch_id} has {len(rows)} rows")
    for row in rows:
        print(row)

process_batch_test(df, 0)
