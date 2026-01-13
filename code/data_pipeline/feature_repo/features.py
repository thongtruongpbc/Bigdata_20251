from datetime import timedelta
from pyspark.sql import DataFrame
import pyspark.sql.functions as F

from feast import Field, FeatureView, Field
from feast.stream_feature_view import stream_feature_view

from feast.types import Int32, Float32
from entities import camera
from data_sources import camera_stats_batch_source, camera_stats_stream_source


# BATCH FEATURE VIEW
camera_stats_view = FeatureView(
    name="camera_stats",
    entities=[camera],
    ttl=timedelta(days=7),
    schema=[
        Field(name="vehicle_count", dtype=Int32),
        Field(name="is_congested", dtype=Int32),
    ],
    online=True,
    source=camera_stats_batch_source,
)


# STREAM FEATURE VIEW (SPARK)
@stream_feature_view(
    entities=[camera],
    ttl=timedelta(days=7),
    mode="spark",
    schema=[
        Field(name="vehicle_count", dtype=Int32),
        Field(name="is_congested", dtype=Int32),
        Field(name="avg_vehicle_count", dtype=Float32),
        Field(name="max_vehicle_count", dtype=Int32),
        Field(name="min_vehicle_count", dtype=Int32),
    ],
    timestamp_field="timestamp",
    online=True,
    source=camera_stats_stream_source,
)
def camera_stats_stream(df: DataFrame) -> DataFrame:
    return (
        df.groupBy(
            F.col("id_camera"),
            F.window(F.col("timestamp"), "10 minutes"),
        )
        .agg(
            F.last("vehicle_count").alias("vehicle_count"),
            F.last("is_congested").alias("is_congested"),
            F.avg("vehicle_count").alias("avg_vehicle_count"),
            F.max("vehicle_count").alias("max_vehicle_count"),
            F.min("vehicle_count").alias("min_vehicle_count"),
            F.max("timestamp").alias("timestamp"),
        )
        .drop("window")
    )