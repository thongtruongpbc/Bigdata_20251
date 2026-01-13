from datetime import timedelta
from feast import FileSource, KafkaSource
from feast.data_format import JsonFormat, ParquetFormat

# 1. Saving offline directory
camera_stats_parquet_file = "data/camera_stats.parquet"

# 2. Batch Source: for training model from historical data
camera_stats_batch_source = FileSource(
    name="camera_stats_batch_source",
    file_format=ParquetFormat(),
    path=camera_stats_parquet_file,
    timestamp_field="timestamp", 
)

# 3. Stream Source
camera_stats_stream_source = KafkaSource(
    name="camera_stats_stream_source",
    kafka_bootstrap_servers="localhost:29092",
    topic="camera_stream",                   
    timestamp_field="timestamp",
    batch_source=camera_stats_batch_source, 
    message_format=JsonFormat(
        schema_json="id_camera string, vehicle_count integer, is_congested integer, timestamp timestamp"
    ),
    watermark_delay_threshold=timedelta(minutes=1), # delay time for data
    description="The Kafka stream containing real-time traffic AI features",
)